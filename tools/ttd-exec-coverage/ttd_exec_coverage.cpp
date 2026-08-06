// SPDX-License-Identifier: MIT
//
// Whole-trace execute-coverage collector built from the design demonstrated by
// Microsoft's WinDbg-Samples TraceAnalysis sample at commit
// 1b0b2f336f959c1caadcd51bb2c82149a9bce2d5.
// https://github.com/microsoft/WinDbg-Samples/blob/1b0b2f336f959c1caadcd51bb2c82149a9bce2d5/TTD/ReplayApi/TraceAnalysis/TraceAnalysis.cpp
//
// Unlike the sample, this collector bounds the execute watchpoint to one
// identity-checked module and uses an atomic byte-coverage bitmap. The bitmap
// is safe under TTD's parallel segment replay and cannot shrink an outer range
// when a later interval is fully contained by it.

#include <TTD/IReplayEngineStl.h>
#include <TTD/IReplayEngineRegisters.h>

#include <Windows.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <memory>
#include <numeric>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <unordered_map>
#include <vector>

namespace
{
using namespace TTD::Replay;
namespace fs = std::filesystem;

constexpr char const* kSchema = "bea.ttd.exec-coverage.v1";
constexpr char const* kCallContextSchema = "bea.ttd.call-context.v3";
constexpr char const* kDataWritesSchema = "bea.ttd.data-writes.v3";
constexpr char const* kDataWritesPromotionPolicy =
    "bea.ttd.data-writes.exact-window-watchpoint-chain.v1";
constexpr uint64_t kDefaultMaxModuleBytes = 1ull << 30;
constexpr uint64_t kDefaultCallContextStackBytes = 64;
constexpr uint64_t kMaxCallContextStackBytes = 256;
constexpr uint64_t kDefaultCallContextEventLimit = 100'000;
constexpr uint64_t kMaxCallContextEventLimit = 1'000'000;
constexpr size_t kMaxDataWriteTargets = 16;
constexpr size_t kMaxDataWriteBytes = 16;

// Measured on TTD Replay 1.11.584.0 (x64), 2026-07-31, against
// G:\bea-ttd\options-open-manual-01\options-open-manual-01.run:
// ICursorView::ReplayResult::StepsExecuted and ::InstructionsExecuted are not
// trustworthy totals on every trace.  That trace's whole-trace replay reported
// 131111 steps against 1137340343 accepted execute-watchpoint callbacks, and
// reported the same 131111 for a 0.2% prefix window - while the single
// sub-window [0x400:0x0, 0x800:0x0) of the same trace reported 3592972 steps.
// A total smaller than one of its own parts is not a wrapped total: the
// engine's step accounting stops advancing in some regions, identically under
// parallel and sequential replay.  Two things follow, and both are done here.
//
//   * Accumulate in 64 bits across step-limited chunks so that nothing this
//     collector controls can wrap.  Verified exact on
//     startup-to-main-menu-20260729-173124: two chunks summing to
//     1860375400, the same value the single unbounded call reported while it
//     was still below 2^32, with byte-identical coverage ranges.
//   * Refuse to publish when the counters that would be written are mutually
//     impossible, instead of emitting another receipt that lies quietly.
//
// The guard is necessary but not sufficient: a frozen counter whose value
// still exceeds callback_hits cannot be detected from the receipt alone.
constexpr uint64_t kReplayChunkSteps = 1'000'000'000;

// Belt and braces against a chunk loop that never reaches a terminal stop
// reason.  At the chunk size above this bounds a run at 10^15 steps.
constexpr uint64_t kMaxReplayChunks = 1'000'000;

struct ReplayAccounting
{
    uint64_t StepsExecuted = 0;
    uint64_t InstructionsExecuted = 0;
    uint64_t ChunkCount = 0;
    EventType StopReason = EventType::Invalid;
};

// Accumulates step-limited replay chunks into 64-bit totals.  NextChunk must
// return an ICursorView::ReplayResult for a replay bounded by
// kReplayChunkSteps steps; it is invoked until a terminal stop reason is
// reported.
template <typename NextChunk>
ReplayAccounting AccumulateReplayChunks(NextChunk&& nextChunk)
{
    ReplayAccounting accounting;
    for (;;)
    {
        ICursorView::ReplayResult const chunk = nextChunk();
        uint64_t const chunkSteps = static_cast<uint64_t>(chunk.StepsExecuted);
        uint64_t const chunkInstructions =
            static_cast<uint64_t>(chunk.InstructionsExecuted);
        if (chunkSteps > kReplayChunkSteps || chunkInstructions > chunkSteps)
        {
            throw std::runtime_error(
                "replay chunk reported more steps than it was allowed to "
                "execute, or more instructions than steps: steps=" +
                std::to_string(chunkSteps) +
                " instructions=" + std::to_string(chunkInstructions));
        }
        accounting.StepsExecuted += chunkSteps;
        accounting.InstructionsExecuted += chunkInstructions;
        accounting.ChunkCount += 1;
        accounting.StopReason = chunk.StopReason;
        if (chunk.StopReason != EventType::StepCount)
        {
            return accounting;
        }
        if (chunkSteps == 0 || accounting.ChunkCount >= kMaxReplayChunks)
        {
            throw std::runtime_error(
                "chunked replay stopped on its step budget without advancing "
                "toward a terminal stop reason after " +
                std::to_string(accounting.ChunkCount) + " chunk(s)");
        }
    }
}

// Written into the receipt beside the withheld counters so a reader learns why
// they are absent without having to reconstruct this investigation.
constexpr char const* kQuarantineReason =
    "ttd-replay-accounting-stopped-advancing";

// A memory-watchpoint execute hit requires an executed instruction, and an
// instruction is a step.  Necessary, not sufficient: a stalled counter whose
// value still exceeds the callback count cannot be caught from the receipt.
bool CountersAreConsistent(
    uint64_t callbackHits,
    uint64_t instructionsExecuted,
    uint64_t stepsExecuted) noexcept
{
    return instructionsExecuted <= stepsExecuted &&
           callbackHits <= instructionsExecuted;
}

// Data-write rows describe a causal transition only while replay remains
// continuous.  Preserve rows across gaps for discovery, but never let a gapful
// history satisfy the collector's promotion check.
bool DataWriteHistoryIsGapFree(
    uint64_t nontrivialGapCount,
    uint64_t continuityBreakCount) noexcept
{
    return nontrivialGapCount == 0 && continuityBreakCount == 0;
}

bool CallContextGapRequiresAssociationBarrier(GapKind kind) noexcept
{
    return kind != GapKind::NoGap;
}

bool CallContextReturnAccountingCloses(
    uint64_t rawReturns,
    uint64_t validatedReturns,
    uint64_t orphanReturns) noexcept
{
    return validatedReturns <= rawReturns &&
           orphanReturns == rawReturns - validatedReturns;
}

bool RunCallContextAssociationTests()
{
    bool const gapPolicy =
        !CallContextGapRequiresAssociationBarrier(GapKind::NoGap) &&
        CallContextGapRequiresAssociationBarrier(GapKind::ContextSwitch) &&
        CallContextGapRequiresAssociationBarrier(GapKind::Unrecorded) &&
        CallContextGapRequiresAssociationBarrier(GapKind::Large);
    bool const returnAccounting =
        CallContextReturnAccountingCloses(3, 2, 1) &&
        CallContextReturnAccountingCloses(0, 0, 0) &&
        !CallContextReturnAccountingCloses(2, 3, 0) &&
        !CallContextReturnAccountingCloses(3, 2, 0);
    if (!gapPolicy || !returnAccounting)
    {
        std::cerr << "call-context association self-test failed\n";
        return false;
    }
    return true;
}

bool RunReplayAccountingTests()
{
    auto fail =
        [](char const* group)
        {
            std::cerr << "replay accounting self-test failed: " << group << "\n";
            return false;
        };

    auto makeChunk =
        [](uint64_t steps, uint64_t instructions, EventType stopReason)
        {
            ICursorView::ReplayResult chunk;
            chunk.StepsExecuted =
                static_cast<decltype(chunk.StepsExecuted)>(steps);
            chunk.InstructionsExecuted =
                static_cast<decltype(chunk.InstructionsExecuted)>(instructions);
            chunk.StopReason = stopReason;
            return chunk;
        };

    auto replayScript =
        [&](std::vector<ICursorView::ReplayResult> script)
        {
            size_t index = 0;
            return AccumulateReplayChunks(
                [&]()
                {
                    if (index >= script.size())
                    {
                        throw std::runtime_error("self-test script exhausted");
                    }
                    return script[index++];
                });
        };

    {
        ReplayAccounting const accounting = replayScript(
            {makeChunk(131'111, 131'110, EventType::Process)});
        if (accounting.StepsExecuted != 131'111 ||
            accounting.InstructionsExecuted != 131'110 ||
            accounting.ChunkCount != 1 ||
            accounting.StopReason != EventType::Process)
        {
            return fail("single terminal chunk");
        }
    }
    {
        // Chosen so that a 32-bit accumulator would land on exactly 131111 -
        // the number options-open-manual-01 published against 1137340343
        // callback hits.  A 64-bit accumulator must land on 2^32 + 131111 and
        // must never be able to produce that receipt's value.
        std::vector<ICursorView::ReplayResult> script;
        for (size_t index = 0; index < 4; ++index)
        {
            script.push_back(
                makeChunk(
                    kReplayChunkSteps,
                    kReplayChunkSteps,
                    EventType::StepCount));
        }
        script.push_back(makeChunk(295'098'407, 295'098'406, EventType::Process));
        ReplayAccounting const accounting = replayScript(std::move(script));
        if (accounting.StepsExecuted != (uint64_t{1} << 32) + 131'111 ||
            accounting.StepsExecuted == 131'111 ||
            accounting.InstructionsExecuted != (uint64_t{1} << 32) + 131'110 ||
            accounting.ChunkCount != 5 ||
            accounting.StopReason != EventType::Process ||
            accounting.StepsExecuted <= 1'137'340'343)
        {
            return fail("64-bit accumulation across the 2^32 boundary");
        }
    }
    {
        bool threw = false;
        try
        {
            replayScript(
                {makeChunk(kReplayChunkSteps, 0, EventType::StepCount),
                 makeChunk(0, 0, EventType::StepCount)});
        }
        catch (std::runtime_error const&)
        {
            threw = true;
        }
        if (!threw)
        {
            return fail("non-advancing chunk must fail closed");
        }
    }
    {
        bool threw = false;
        try
        {
            replayScript(
                {makeChunk(kReplayChunkSteps + 1, 0, EventType::Process)});
        }
        catch (std::runtime_error const&)
        {
            threw = true;
        }
        if (!threw)
        {
            return fail("over-budget chunk must fail closed");
        }
    }
    {
        bool threw = false;
        try
        {
            replayScript({makeChunk(10, 11, EventType::Process)});
        }
        catch (std::runtime_error const&)
        {
            threw = true;
        }
        if (!threw)
        {
            return fail("instructions above steps must fail closed");
        }
    }
    {
        // The two recorded receipts that this guard exists to reject, and the
        // healthy startup receipt it must keep accepting.
        if (CountersAreConsistent(1'137'340'343, 131'110, 131'111) ||
            CountersAreConsistent(245'245'503, 137'022, 137'023) ||
            !CountersAreConsistent(715'094'340, 1'860'375'340, 1'860'375'400) ||
            !CountersAreConsistent(0, 0, 0) ||
            !CountersAreConsistent(5, 5, 5) ||
            CountersAreConsistent(0, 6, 5))
        {
            return fail("recorded impossible and healthy counter triples");
        }
    }
    return true;
}

struct Range
{
    uint64_t Min;
    uint64_t Max;

    friend bool operator==(Range const&, Range const&) = default;
};

enum class AnalysisMode
{
    Coverage,
    CallContext,
    DataWrites,
};

struct CallContextTarget
{
    uint64_t EntryRva = 0;
    std::vector<Range> Ranges;
    std::optional<uint64_t> ExpectedEntryCount;
    std::optional<uint64_t> ExpectedCallCount;
    std::optional<uint64_t> ExpectedReturnCount;
};

struct DataWriteTarget
{
    uint64_t Address = 0;
    uint64_t Size = 0;
    std::optional<uint64_t> ExpectedOverwriteCount;
    std::optional<uint64_t> ExpectedWriteCount;
};

std::vector<CallContextTarget> ParseCallContextTargets(std::istream& input);
std::vector<DataWriteTarget> ParseDataWriteTargets(std::istream& input);
std::vector<size_t> FindDataWriteIntersections(
    std::vector<DataWriteTarget> const& targets,
    uint64_t address,
    uint64_t size);
bool RunDataWriteEvidenceTests();

std::vector<Range> CoalesceHalfOpenRanges(std::vector<Range> ranges)
{
    std::erase_if(ranges, [](Range const& range) { return range.Min >= range.Max; });
    std::sort(
        ranges.begin(),
        ranges.end(),
        [](Range const& left, Range const& right)
        {
            return left.Min < right.Min ||
                   (left.Min == right.Min && left.Max < right.Max);
        });

    std::vector<Range> merged;
    for (Range const& next : ranges)
    {
        if (merged.empty() || next.Min > merged.back().Max)
        {
            merged.push_back(next);
            continue;
        }

        // The upstream sample assigned next.Max here. max() is essential when
        // next is fully contained by the current range.
        merged.back().Max = std::max(merged.back().Max, next.Max);
    }
    return merged;
}

bool RunAtomicCoverageTests();

bool RunCallContextTargetTests()
{
    auto parse =
        [](std::string const& text)
        {
            std::istringstream input(text);
            return ParseCallContextTargets(input);
        };
    auto rejects =
        [&](std::string const& text)
        {
            try
            {
                parse(text);
                return false;
            }
            catch (std::exception const&)
            {
                return true;
            }
        };
    std::string const header =
        "target_index\tentry_rva\trange_start_rva\t"
        "range_end_rva_exclusive\texpected_entry_count\t"
        "expected_call_count\texpected_return_count\n";
    auto const valid = parse(
        header +
        "0\t0x10\t0x10\t0x20\t1\t1\t1\n"
        "0\t0x10\t0x30\t0x40\t1\t1\t1\n"
        "1\t0x50\t0x50\t0x60\t\t\t\n");
    if (valid.size() != 2 || valid[0].Ranges.size() != 2 ||
        valid[0].EntryRva != 0x10 || valid[0].ExpectedCallCount != 1 ||
        valid[1].ExpectedCallCount.has_value())
    {
        std::cerr << "call-context target self-test failed: valid table\n";
        return false;
    }
    if (!rejects("wrong\n") ||
        !rejects(header + "1\t0x10\t0x10\t0x20\t\t\t\n") ||
        !rejects(
            header +
            "0\t0x10\t0x10\t0x20\t1\t1\t1\n"
            "0\t0x10\t0x18\t0x30\t1\t1\t1\n") ||
        !rejects(header + "0\t0x25\t0x10\t0x20\t\t\t\n") ||
        !rejects(
            header +
            "0\t0x10\t0x10\t0x20\t1\t1\t1\n"
            "0\t0x10\t0x30\t0x40\t2\t1\t1\n"))
    {
        std::cerr << "call-context target self-test failed: poison table\n";
        return false;
    }
    return true;
}

bool RunDataWriteTargetTests()
{
    auto parse =
        [](std::string const& text)
        {
            std::istringstream input(text);
            return ParseDataWriteTargets(input);
        };
    auto rejects =
        [&](std::string const& text)
        {
            try
            {
                parse(text);
                return false;
            }
            catch (std::exception const&)
            {
                return true;
            }
        };
    std::string const header =
        "target_index\taddress\tsize\texpected_overwrite_count\t"
        "expected_write_count\n";
    auto const valid = parse(
        header +
        "0\t0x89D950\t4\t2\t2\n"
        "1\t0x5DBAE4\t4\t0\t0\n");
    if (valid.size() != 2 || valid[0].Address != 0x89D950 ||
        valid[0].Size != 4 || valid[0].ExpectedWriteCount != 2 ||
        valid[1].ExpectedOverwriteCount != 0)
    {
        std::cerr << "data-write target self-test failed: valid table\n";
        return false;
    }
    if (!rejects("wrong\n") ||
        !rejects(header + "1\t0x1000\t4\t\t\n") ||
        !rejects(header + "0\t0x1000\t0\t\t\n") ||
        !rejects(header + "0\t0x1000\t17\t\t\n") ||
        !rejects(header + "0\t0xFFFFFFFD\t4\t\t\n") ||
        !rejects(
            header +
            "0\t0x1000\t4\t\t\n"
            "1\t0x1002\t4\t\t\n"))
    {
        std::cerr << "data-write target self-test failed: poison table\n";
        return false;
    }
    if (FindDataWriteIntersections(valid, 0x89D950, 4) !=
            std::vector<size_t>{0} ||
        FindDataWriteIntersections(valid, 0x89D951, 1) !=
            std::vector<size_t>{0} ||
        !FindDataWriteIntersections(valid, 0x89D960, 4).empty() ||
        !FindDataWriteIntersections(valid, 0x89D950, 0).empty() ||
        !FindDataWriteIntersections(
             valid,
             std::numeric_limits<uint64_t>::max() - 1,
             4).empty())
    {
        std::cerr << "data-write target self-test failed: intersections\n";
        return false;
    }
    std::vector<DataWriteTarget> const adjacent{
        {.Address = 0x1000, .Size = 4},
        {.Address = 0x1004, .Size = 4},
    };
    if (FindDataWriteIntersections(adjacent, 0x1002, 4) !=
        std::vector<size_t>{0, 1})
    {
        std::cerr << "data-write target self-test failed: ambiguous access\n";
        return false;
    }
    if (!DataWriteHistoryIsGapFree(0, 0) ||
        DataWriteHistoryIsGapFree(1, 0) ||
        DataWriteHistoryIsGapFree(0, 1) ||
        DataWriteHistoryIsGapFree(1, 1))
    {
        std::cerr << "data-write target self-test failed: gap policy\n";
        return false;
    }
    return true;
}

bool RunSelfTests()
{
    struct Case
    {
        std::vector<Range> Input;
        std::vector<Range> Expected;
    };

    std::vector<Case> const cases
    {
        {.Input = {}, .Expected = {}},
        {.Input = {{10, 20}}, .Expected = {{10, 20}}},
        {.Input = {{10, 20}, {30, 40}}, .Expected = {{10, 20}, {30, 40}}},
        {.Input = {{10, 20}, {20, 30}}, .Expected = {{10, 30}}},
        {.Input = {{10, 30}, {20, 40}}, .Expected = {{10, 40}}},
        {.Input = {{10, 100}, {20, 30}}, .Expected = {{10, 100}}},
        {.Input = {{20, 30}, {10, 100}}, .Expected = {{10, 100}}},
        {.Input = {{10, 20}, {10, 30}, {30, 40}}, .Expected = {{10, 40}}},
        {.Input = {{5, 5}, {9, 2}, {1, 2}, {1, 2}}, .Expected = {{1, 2}}},
    };

    for (size_t index = 0; index < cases.size(); ++index)
    {
        auto const actual = CoalesceHalfOpenRanges(cases[index].Input);
        if (actual != cases[index].Expected)
        {
            std::cerr << "self-test case " << index << " failed\n";
            return false;
        }
    }

    if (!RunAtomicCoverageTests())
    {
        return false;
    }

    if (!RunReplayAccountingTests())
    {
        return false;
    }

    if (!RunCallContextTargetTests())
    {
        return false;
    }

    if (!RunCallContextAssociationTests())
    {
        return false;
    }

    if (!RunDataWriteTargetTests())
    {
        return false;
    }

    if (!RunDataWriteEvidenceTests())
    {
        return false;
    }

    std::cout
        << "self-test: 9/9 coalescing and 6/6 bitmap groups passed; "
        << "containment, clipping, boundaries, randomized parity, and "
        << "concurrent atomic OR are preserved\n"
        << "self-test: 6/6 replay-accounting groups passed; chunked totals "
        << "cross 2^32 in 64 bits, non-advancing or impossible chunks fail "
        << "closed, and both recorded impossible counter triples are "
        << "rejected while the healthy one is accepted\n";
    std::cout
        << "self-test: call-context target tables preserve grouped exact ranges "
        << "and reject bad headers, gaps, overlaps, orphan entries, and "
        << "inconsistent expectations; global association barriers and "
        << "return/orphan accounting close\n";
    std::cout
        << "self-test: data-write target tables preserve bounded x86 ranges "
        << "and reject malformed, overlapping, overflowing, or oversized "
        << "targets; any replay gap or continuity break fails promotion\n"
        << "self-test: data-write evidence requires explicit counts and either "
        << "an event-sourced ordered write chain or a bounded zero-callback "
        << "witness\n";
    return true;
}

std::string ToUtf8(std::wstring_view value)
{
    if (value.empty())
    {
        return {};
    }
    if (value.size() > static_cast<size_t>(std::numeric_limits<int>::max()))
    {
        throw std::runtime_error("UTF-16 input is too large");
    }

    int const length = static_cast<int>(value.size());
    int const required = WideCharToMultiByte(
        CP_UTF8,
        WC_ERR_INVALID_CHARS,
        value.data(),
        length,
        nullptr,
        0,
        nullptr,
        nullptr);
    if (required <= 0)
    {
        throw std::runtime_error("WideCharToMultiByte size query failed");
    }

    std::string result(static_cast<size_t>(required), '\0');
    int const written = WideCharToMultiByte(
        CP_UTF8,
        WC_ERR_INVALID_CHARS,
        value.data(),
        length,
        result.data(),
        required,
        nullptr,
        nullptr);
    if (written != required)
    {
        throw std::runtime_error("WideCharToMultiByte conversion failed");
    }
    return result;
}

std::string JsonEscape(std::string_view value)
{
    std::ostringstream output;
    for (unsigned char const ch : value)
    {
        switch (ch)
        {
        case '"': output << "\\\""; break;
        case '\\': output << "\\\\"; break;
        case '\b': output << "\\b"; break;
        case '\f': output << "\\f"; break;
        case '\n': output << "\\n"; break;
        case '\r': output << "\\r"; break;
        case '\t': output << "\\t"; break;
        default:
            if (ch < 0x20)
            {
                output << "\\u"
                       << std::hex << std::uppercase << std::setfill('0')
                       << std::setw(4) << static_cast<unsigned int>(ch)
                       << std::dec;
            }
            else
            {
                output << static_cast<char>(ch);
            }
            break;
        }
    }
    return output.str();
}

std::string JsonEscape(std::wstring_view value)
{
    return JsonEscape(ToUtf8(value));
}

std::string Hex(uint64_t value)
{
    std::ostringstream output;
    output << "0x" << std::hex << std::uppercase << value;
    return output.str();
}

std::string PositionString(Position const& position)
{
    return Hex(static_cast<uint64_t>(position.Sequence)) + ":" +
           Hex(static_cast<uint64_t>(position.Steps));
}

bool EqualOrdinalIgnoreCase(std::wstring_view left, std::wstring_view right)
{
    if (left.size() != right.size())
    {
        return false;
    }
    if (left.empty())
    {
        return true;
    }
    if (left.size() > static_cast<size_t>(std::numeric_limits<int>::max()))
    {
        return false;
    }
    return CompareStringOrdinal(
               left.data(),
               static_cast<int>(left.size()),
               right.data(),
               static_cast<int>(right.size()),
               TRUE) == CSTR_EQUAL;
}

uint64_t ParseNumber(std::wstring const& text, std::wstring const& option)
{
    if (text.empty() || text.front() == L'-')
    {
        throw std::runtime_error(
            "invalid non-negative numeric value for " +
            ToUtf8(option) + ": " + ToUtf8(text));
    }
    size_t consumed = 0;
    uint64_t const value = std::stoull(text, &consumed, 0);
    if (consumed != text.size())
    {
        throw std::runtime_error(
            "invalid numeric value for " + ToUtf8(option) + ": " + ToUtf8(text));
    }
    return value;
}

Position ParsePosition(std::wstring const& text, std::wstring const& option)
{
    size_t const separator = text.find(L':');
    if (separator == std::wstring::npos ||
        text.find(L':', separator + 1) != std::wstring::npos)
    {
        throw std::runtime_error(
            "position for " + ToUtf8(option) + " must be SEQUENCE:STEPS");
    }
    std::wstring const sequenceText = text.substr(0, separator);
    std::wstring const stepsText = text.substr(separator + 1);
    if (sequenceText.empty() || stepsText.empty())
    {
        throw std::runtime_error(
            "position for " + ToUtf8(option) + " must be SEQUENCE:STEPS");
    }
    uint64_t const sequence = ParseNumber(sequenceText, option);
    uint64_t const steps = ParseNumber(stepsText, option);
    if (sequence > static_cast<uint64_t>(TTD::SequenceId::Max) ||
        steps > static_cast<uint64_t>(StepCount::Max))
    {
        throw std::runtime_error(
            "position for " + ToUtf8(option) + " is outside the valid range");
    }
    return Position{
        static_cast<TTD::SequenceId>(sequence),
        static_cast<StepCount>(steps),
    };
}

std::vector<std::string> SplitTsv(std::string const& line)
{
    std::vector<std::string> fields;
    size_t start = 0;
    for (;;)
    {
        size_t const separator = line.find('\t', start);
        if (separator == std::string::npos)
        {
            fields.push_back(line.substr(start));
            return fields;
        }
        fields.push_back(line.substr(start, separator - start));
        start = separator + 1;
    }
}

uint64_t ParseAsciiNumber(std::string const& text, char const* field)
{
    if (text.empty() || text.front() == '-')
    {
        throw std::runtime_error(
            std::string("invalid non-negative numeric value for ") + field);
    }
    size_t consumed = 0;
    uint64_t const value = std::stoull(text, &consumed, 0);
    if (consumed != text.size())
    {
        throw std::runtime_error(
            std::string("invalid numeric value for ") + field + ": " + text);
    }
    return value;
}

std::optional<uint64_t> ParseOptionalAsciiNumber(
    std::string const& text,
    char const* field)
{
    if (text.empty())
    {
        return std::nullopt;
    }
    return ParseAsciiNumber(text, field);
}

std::vector<CallContextTarget> ParseCallContextTargets(std::istream& input)
{
    constexpr char const* expectedHeader =
        "target_index\tentry_rva\trange_start_rva\t"
        "range_end_rva_exclusive\texpected_entry_count\t"
        "expected_call_count\texpected_return_count";

    std::string line;
    if (!std::getline(input, line))
    {
        throw std::runtime_error("call-context target table is empty");
    }
    if (!line.empty() && line.back() == '\r')
    {
        line.pop_back();
    }
    if (line != expectedHeader)
    {
        throw std::runtime_error(
            "call-context target table has an unexpected header");
    }

    std::vector<CallContextTarget> targets;
    size_t lineNumber = 1;
    size_t previousIndex = 0;
    bool havePreviousIndex = false;
    while (std::getline(input, line))
    {
        ++lineNumber;
        if (!line.empty() && line.back() == '\r')
        {
            line.pop_back();
        }
        if (line.empty())
        {
            throw std::runtime_error(
                "call-context target table contains a blank row at line " +
                std::to_string(lineNumber));
        }
        std::vector<std::string> const fields = SplitTsv(line);
        if (fields.size() != 7)
        {
            throw std::runtime_error(
                "call-context target row must contain exactly seven fields at line " +
                std::to_string(lineNumber));
        }

        uint64_t const rawIndex = ParseAsciiNumber(fields[0], "target_index");
        if (rawIndex > std::numeric_limits<size_t>::max())
        {
            throw std::runtime_error("call-context target index is too large");
        }
        size_t const index = static_cast<size_t>(rawIndex);
        if ((havePreviousIndex && index < previousIndex) || index > targets.size())
        {
            throw std::runtime_error(
                "call-context target indices must be contiguous and grouped");
        }
        previousIndex = index;
        havePreviousIndex = true;

        uint64_t const entry = ParseAsciiNumber(fields[1], "entry_rva");
        Range const range{
            ParseAsciiNumber(fields[2], "range_start_rva"),
            ParseAsciiNumber(fields[3], "range_end_rva_exclusive"),
        };
        if (range.Min >= range.Max)
        {
            throw std::runtime_error(
                "call-context target range must be non-empty and half-open");
        }
        std::optional<uint64_t> const expectedEntry =
            ParseOptionalAsciiNumber(fields[4], "expected_entry_count");
        std::optional<uint64_t> const expectedCall =
            ParseOptionalAsciiNumber(fields[5], "expected_call_count");
        std::optional<uint64_t> const expectedReturn =
            ParseOptionalAsciiNumber(fields[6], "expected_return_count");

        if (index == targets.size())
        {
            targets.push_back(
                CallContextTarget{
                    .EntryRva = entry,
                    .Ranges = {},
                    .ExpectedEntryCount = expectedEntry,
                    .ExpectedCallCount = expectedCall,
                    .ExpectedReturnCount = expectedReturn,
                });
        }
        CallContextTarget& target = targets[index];
        if (target.EntryRva != entry ||
            target.ExpectedEntryCount != expectedEntry ||
            target.ExpectedCallCount != expectedCall ||
            target.ExpectedReturnCount != expectedReturn)
        {
            throw std::runtime_error(
                "repeated call-context target rows disagree on identity or expectations");
        }
        if (!target.Ranges.empty() && range.Min < target.Ranges.back().Max)
        {
            throw std::runtime_error(
                "call-context target ranges must be sorted and non-overlapping");
        }
        target.Ranges.push_back(range);
    }

    if (targets.empty())
    {
        throw std::runtime_error("call-context target table contains no targets");
    }
    if (targets.size() > 4096)
    {
        throw std::runtime_error("call-context target table exceeds 4096 targets");
    }
    for (CallContextTarget const& target : targets)
    {
        size_t containingRangeCount = 0;
        for (Range const& range : target.Ranges)
        {
            if (target.EntryRva >= range.Min && target.EntryRva < range.Max)
            {
                ++containingRangeCount;
            }
        }
        if (containingRangeCount != 1)
        {
            throw std::runtime_error(
                "each call-context entry must belong to exactly one target range");
        }
    }
    return targets;
}

std::vector<CallContextTarget> ReadCallContextTargets(fs::path const& path)
{
    std::ifstream input(path, std::ios::binary | std::ios::in);
    if (!input)
    {
        throw std::runtime_error("failed to open call-context target table");
    }
    return ParseCallContextTargets(input);
}

std::vector<DataWriteTarget> ParseDataWriteTargets(std::istream& input)
{
    constexpr char const* expectedHeader =
        "target_index\taddress\tsize\texpected_overwrite_count\t"
        "expected_write_count";

    std::string line;
    if (!std::getline(input, line))
    {
        throw std::runtime_error("data-write target table is empty");
    }
    if (!line.empty() && line.back() == '\r')
    {
        line.pop_back();
    }
    if (line != expectedHeader)
    {
        throw std::runtime_error(
            "data-write target table has an unexpected header");
    }

    std::vector<DataWriteTarget> targets;
    size_t lineNumber = 1;
    while (std::getline(input, line))
    {
        ++lineNumber;
        if (!line.empty() && line.back() == '\r')
        {
            line.pop_back();
        }
        if (line.empty())
        {
            throw std::runtime_error(
                "data-write target table contains a blank row at line " +
                std::to_string(lineNumber));
        }
        std::vector<std::string> const fields = SplitTsv(line);
        if (fields.size() != 5)
        {
            throw std::runtime_error(
                "data-write target row must contain exactly five fields at line " +
                std::to_string(lineNumber));
        }
        uint64_t const rawIndex = ParseAsciiNumber(fields[0], "target_index");
        if (rawIndex != targets.size())
        {
            throw std::runtime_error(
                "data-write target indices must be contiguous and unique");
        }
        uint64_t const address = ParseAsciiNumber(fields[1], "address");
        uint64_t const size = ParseAsciiNumber(fields[2], "size");
        constexpr uint64_t x86AddressSpace = uint64_t{1} << 32;
        if (address == 0 || address >= x86AddressSpace || size == 0 ||
            size > kMaxDataWriteBytes || size > x86AddressSpace - address)
        {
            throw std::runtime_error(
                "data-write target must be a non-empty 1..16 byte x86 range");
        }
        targets.push_back(
            DataWriteTarget{
                .Address = address,
                .Size = size,
                .ExpectedOverwriteCount = ParseOptionalAsciiNumber(
                    fields[3], "expected_overwrite_count"),
                .ExpectedWriteCount = ParseOptionalAsciiNumber(
                    fields[4], "expected_write_count"),
            });
    }
    if (targets.empty())
    {
        throw std::runtime_error("data-write target table contains no targets");
    }
    if (targets.size() > kMaxDataWriteTargets)
    {
        throw std::runtime_error("data-write target table exceeds 16 targets");
    }
    for (size_t left = 0; left < targets.size(); ++left)
    {
        uint64_t const leftEnd = targets[left].Address + targets[left].Size;
        for (size_t right = left + 1; right < targets.size(); ++right)
        {
            uint64_t const rightEnd = targets[right].Address + targets[right].Size;
            if (targets[left].Address < rightEnd &&
                targets[right].Address < leftEnd)
            {
                throw std::runtime_error(
                    "data-write target ranges overlap; split the batch");
            }
        }
    }
    return targets;
}

std::vector<DataWriteTarget> ReadDataWriteTargets(fs::path const& path)
{
    std::ifstream input(path, std::ios::binary | std::ios::in);
    if (!input)
    {
        throw std::runtime_error("failed to open data-write target table");
    }
    return ParseDataWriteTargets(input);
}

std::vector<size_t> FindDataWriteIntersections(
    std::vector<DataWriteTarget> const& targets,
    uint64_t address,
    uint64_t size)
{
    std::vector<size_t> intersections;
    if (size == 0 || size > std::numeric_limits<uint64_t>::max() - address)
    {
        return intersections;
    }
    uint64_t const end = address + size;
    for (size_t index = 0; index < targets.size(); ++index)
    {
        DataWriteTarget const& target = targets[index];
        uint64_t const targetEnd = target.Address + target.Size;
        if (address < targetEnd && target.Address < end)
        {
            intersections.push_back(index);
        }
    }
    return intersections;
}

struct Options
{
    AnalysisMode Mode = AnalysisMode::Coverage;
    bool SelfTest = false;
    bool Sequential = false;
    bool QuarantineCounters = false;
    fs::path Trace;
    fs::path Output;
    std::wstring ModuleName;
    std::optional<uint64_t> ExpectedBase;
    std::optional<uint64_t> ExpectedSize;
    std::optional<uint64_t> ExpectedTimestamp;
    std::optional<uint64_t> ExpectedChecksum;
    std::optional<Position> From;
    std::optional<Position> To;
    uint64_t MaxModuleBytes = kDefaultMaxModuleBytes;
    std::vector<uint64_t> MustHitRvas;
    std::vector<uint64_t> MustMissRvas;
    fs::path CallContextTargets;
    fs::path DataWriteTargets;
    uint64_t CallContextStackBytes = kDefaultCallContextStackBytes;
    uint64_t CallContextEventLimit = kDefaultCallContextEventLimit;
};

void PrintUsage()
{
    std::cerr
        << "Usage:\n"
        << "  ttd_exec_coverage --self-test\n"
        << "  ttd_exec_coverage [--mode coverage] --trace FILE --module NAME --out FILE\n"
        << "    --expect-size NUMBER --expect-timestamp NUMBER"
        << " --expect-checksum NUMBER [options]\n\n"
        << "  ttd_exec_coverage --mode call-context --trace FILE --module NAME\n"
        << "    --out FILE --targets-tsv FILE --expect-size NUMBER\n"
        << "    --expect-timestamp NUMBER --expect-checksum NUMBER [options]\n\n"
        << "  ttd_exec_coverage --mode data-writes --trace FILE --module NAME\n"
        << "    --out FILE --data-targets-tsv FILE --from SEQUENCE:STEPS\n"
        << "    --to SEQUENCE:STEPS --expect-size NUMBER\n"
        << "    --expect-timestamp NUMBER --expect-checksum NUMBER [options]\n\n"
        << "Options:\n"
        << "  --mode coverage|call-context|data-writes\n"
        << "  --expect-base NUMBER\n"
        << "  --from SEQUENCE:STEPS\n"
        << "  --to SEQUENCE:STEPS\n"
        << "  --sequential\n"
        << "  --quarantine-counters      publish coverage with the step and\n"
        << "                             callback counters withheld when the\n"
        << "                             replay engine's accounting is\n"
        << "                             impossible, instead of refusing to\n"
        << "                             publish (exit 11)\n"
        << "  --max-module-bytes NUMBER\n"
        << "  --must-hit-rva NUMBER      (repeatable)\n"
        << "  --must-miss-rva NUMBER     (repeatable)\n"
        << "Call-context-only options:\n"
        << "  --targets-tsv FILE\n"
        << "  --stack-bytes NUMBER       (1..256; default 64)\n"
        << "Call-context/data-write options:\n"
        << "  --event-limit NUMBER       (1..1000000; default 100000)\n"
        << "Data-write-only options:\n"
        << "  --data-targets-tsv FILE\n";
}

Options ParseOptions(int argc, wchar_t* argv[])
{
    Options options;
    bool maxModuleBytesSet = false;
    bool modeSet = false;
    bool stackBytesSet = false;
    bool eventLimitSet = false;

    auto requireValue =
        [&](int& index, std::wstring const& option) -> std::wstring
        {
            if (index + 1 >= argc)
            {
                throw std::runtime_error("missing value for " + ToUtf8(option));
            }
            return argv[++index];
        };

    for (int index = 1; index < argc; ++index)
    {
        std::wstring const option = argv[index];
        if (option == L"--self-test")
        {
            options.SelfTest = true;
        }
        else if (option == L"--mode")
        {
            if (modeSet)
            {
                throw std::runtime_error("duplicate option: --mode");
            }
            modeSet = true;
            std::wstring const value = requireValue(index, option);
            if (value == L"coverage")
            {
                options.Mode = AnalysisMode::Coverage;
            }
            else if (value == L"call-context")
            {
                options.Mode = AnalysisMode::CallContext;
            }
            else if (value == L"data-writes")
            {
                options.Mode = AnalysisMode::DataWrites;
            }
            else
            {
                throw std::runtime_error(
                    "--mode must be coverage, call-context, or data-writes");
            }
        }
        else if (option == L"--sequential")
        {
            if (options.Sequential)
            {
                throw std::runtime_error("duplicate option: --sequential");
            }
            options.Sequential = true;
        }
        else if (option == L"--quarantine-counters")
        {
            if (options.QuarantineCounters)
            {
                throw std::runtime_error(
                    "duplicate option: --quarantine-counters");
            }
            options.QuarantineCounters = true;
        }
        else if (option == L"--trace")
        {
            if (!options.Trace.empty())
            {
                throw std::runtime_error("duplicate option: --trace");
            }
            options.Trace = requireValue(index, option);
        }
        else if (option == L"--module")
        {
            if (!options.ModuleName.empty())
            {
                throw std::runtime_error("duplicate option: --module");
            }
            options.ModuleName = requireValue(index, option);
        }
        else if (option == L"--out")
        {
            if (!options.Output.empty())
            {
                throw std::runtime_error("duplicate option: --out");
            }
            options.Output = requireValue(index, option);
        }
        else if (option == L"--expect-base")
        {
            if (options.ExpectedBase)
            {
                throw std::runtime_error("duplicate option: --expect-base");
            }
            options.ExpectedBase = ParseNumber(requireValue(index, option), option);
        }
        else if (option == L"--expect-size")
        {
            if (options.ExpectedSize)
            {
                throw std::runtime_error("duplicate option: --expect-size");
            }
            options.ExpectedSize = ParseNumber(requireValue(index, option), option);
        }
        else if (option == L"--expect-timestamp")
        {
            if (options.ExpectedTimestamp)
            {
                throw std::runtime_error("duplicate option: --expect-timestamp");
            }
            options.ExpectedTimestamp =
                ParseNumber(requireValue(index, option), option);
        }
        else if (option == L"--expect-checksum")
        {
            if (options.ExpectedChecksum)
            {
                throw std::runtime_error("duplicate option: --expect-checksum");
            }
            options.ExpectedChecksum =
                ParseNumber(requireValue(index, option), option);
        }
        else if (option == L"--from")
        {
            if (options.From)
            {
                throw std::runtime_error("duplicate option: --from");
            }
            options.From = ParsePosition(requireValue(index, option), option);
        }
        else if (option == L"--to")
        {
            if (options.To)
            {
                throw std::runtime_error("duplicate option: --to");
            }
            options.To = ParsePosition(requireValue(index, option), option);
        }
        else if (option == L"--max-module-bytes")
        {
            if (maxModuleBytesSet)
            {
                throw std::runtime_error("duplicate option: --max-module-bytes");
            }
            maxModuleBytesSet = true;
            options.MaxModuleBytes =
                ParseNumber(requireValue(index, option), option);
        }
        else if (option == L"--must-hit-rva")
        {
            options.MustHitRvas.push_back(
                ParseNumber(requireValue(index, option), option));
        }
        else if (option == L"--must-miss-rva")
        {
            options.MustMissRvas.push_back(
                ParseNumber(requireValue(index, option), option));
        }
        else if (option == L"--targets-tsv")
        {
            if (!options.CallContextTargets.empty())
            {
                throw std::runtime_error("duplicate option: --targets-tsv");
            }
            options.CallContextTargets = requireValue(index, option);
        }
        else if (option == L"--data-targets-tsv")
        {
            if (!options.DataWriteTargets.empty())
            {
                throw std::runtime_error(
                    "duplicate option: --data-targets-tsv");
            }
            options.DataWriteTargets = requireValue(index, option);
        }
        else if (option == L"--stack-bytes")
        {
            if (stackBytesSet)
            {
                throw std::runtime_error("duplicate option: --stack-bytes");
            }
            stackBytesSet = true;
            options.CallContextStackBytes =
                ParseNumber(requireValue(index, option), option);
        }
        else if (option == L"--event-limit")
        {
            if (eventLimitSet)
            {
                throw std::runtime_error("duplicate option: --event-limit");
            }
            eventLimitSet = true;
            options.CallContextEventLimit =
                ParseNumber(requireValue(index, option), option);
        }
        else
        {
            throw std::runtime_error("unknown option: " + ToUtf8(option));
        }
    }

    if (options.SelfTest)
    {
        if (argc != 2)
        {
            throw std::runtime_error("--self-test cannot be combined with other options");
        }
        return options;
    }

    if (options.Trace.empty() || options.ModuleName.empty() || options.Output.empty())
    {
        throw std::runtime_error("--trace, --module, and --out are required");
    }
    if (!options.ExpectedSize ||
        !options.ExpectedTimestamp ||
        !options.ExpectedChecksum)
    {
        throw std::runtime_error(
            "--expect-size, --expect-timestamp, and --expect-checksum are required");
    }
    if (*options.ExpectedSize == 0 || options.MaxModuleBytes == 0)
    {
        throw std::runtime_error("module size limits must be positive");
    }
    if (*options.ExpectedTimestamp > std::numeric_limits<uint32_t>::max() ||
        *options.ExpectedChecksum > std::numeric_limits<uint32_t>::max())
    {
        throw std::runtime_error("timestamp and checksum must fit in 32 bits");
    }
    if (options.From && options.To && *options.From > *options.To)
    {
        throw std::runtime_error("--from must not be after --to");
    }

    if (options.Mode == AnalysisMode::Coverage)
    {
        if (!options.CallContextTargets.empty() ||
            !options.DataWriteTargets.empty() || stackBytesSet || eventLimitSet)
        {
            throw std::runtime_error(
                "semantic replay options require call-context or data-writes mode");
        }
    }
    else if (options.Mode == AnalysisMode::CallContext)
    {
        if (options.CallContextTargets.empty() ||
            !options.DataWriteTargets.empty())
        {
            throw std::runtime_error(
                "--targets-tsv is required in call-context mode");
        }
        if (options.Sequential || options.QuarantineCounters ||
            !options.MustHitRvas.empty() || !options.MustMissRvas.empty())
        {
            throw std::runtime_error(
                "coverage-only switches cannot be combined with call-context mode");
        }
        if (options.CallContextStackBytes == 0 ||
            options.CallContextStackBytes > kMaxCallContextStackBytes)
        {
            throw std::runtime_error(
                "--stack-bytes must be between 1 and 256");
        }
        if (options.CallContextEventLimit == 0 ||
            options.CallContextEventLimit > kMaxCallContextEventLimit)
        {
            throw std::runtime_error(
                "--event-limit must be between 1 and 1000000");
        }
    }
    else
    {
        if (options.DataWriteTargets.empty() ||
            !options.CallContextTargets.empty())
        {
            throw std::runtime_error(
                "--data-targets-tsv is required in data-writes mode");
        }
        if (!options.From || !options.To)
        {
            throw std::runtime_error(
                "data-writes mode requires explicit --from and --to bounds");
        }
        if (options.Sequential || options.QuarantineCounters || stackBytesSet ||
            !options.MustHitRvas.empty() || !options.MustMissRvas.empty())
        {
            throw std::runtime_error(
                "coverage/call-context-only switches cannot be combined with data-writes mode");
        }
        if (options.CallContextEventLimit == 0 ||
            options.CallContextEventLimit > kMaxCallContextEventLimit)
        {
            throw std::runtime_error(
                "--event-limit must be between 1 and 1000000");
        }
    }

    options.Trace = fs::absolute(options.Trace).lexically_normal();
    options.Output = fs::absolute(options.Output).lexically_normal();
    if (EqualOrdinalIgnoreCase(options.Trace.native(), options.Output.native()))
    {
        throw std::runtime_error("trace and output paths must differ");
    }
    if (!fs::is_regular_file(options.Trace))
    {
        throw std::runtime_error("trace is not a regular file");
    }
    if (fs::exists(options.Output))
    {
        throw std::runtime_error("output already exists");
    }
    if (options.Mode == AnalysisMode::CallContext)
    {
        options.CallContextTargets =
            fs::absolute(options.CallContextTargets).lexically_normal();
        if (!fs::is_regular_file(options.CallContextTargets))
        {
            throw std::runtime_error(
                "call-context target table is not a regular file");
        }
        if (EqualOrdinalIgnoreCase(
                options.Trace.native(),
                options.CallContextTargets.native()) ||
            EqualOrdinalIgnoreCase(
                options.Output.native(),
                options.CallContextTargets.native()))
        {
            throw std::runtime_error(
                "trace, output, and call-context target paths must differ");
        }
    }
    else if (options.Mode == AnalysisMode::DataWrites)
    {
        options.DataWriteTargets =
            fs::absolute(options.DataWriteTargets).lexically_normal();
        if (!fs::is_regular_file(options.DataWriteTargets))
        {
            throw std::runtime_error(
                "data-write target table is not a regular file");
        }
        if (EqualOrdinalIgnoreCase(
                options.Trace.native(),
                options.DataWriteTargets.native()) ||
            EqualOrdinalIgnoreCase(
                options.Output.native(),
                options.DataWriteTargets.native()))
        {
            throw std::runtime_error(
                "trace, output, and data-write target paths must differ");
        }
    }
    for (uint64_t const rva : options.MustHitRvas)
    {
        if (std::find(
                options.MustMissRvas.begin(),
                options.MustMissRvas.end(),
                rva) != options.MustMissRvas.end())
        {
            throw std::runtime_error(
                "one RVA cannot be both a required hit and required miss: " +
                Hex(rva));
        }
    }
    return options;
}

class AtomicCoverage
{
public:
    AtomicCoverage(uint64_t base, uint64_t size)
        : m_base(base),
          m_size(size),
          m_wordCount(static_cast<size_t>((size + 63) / 64)),
          m_words(std::make_unique<std::atomic<uint64_t>[]>(m_wordCount))
    {
        static_assert(std::atomic<uint64_t>::is_always_lock_free);
        for (size_t index = 0; index < m_wordCount; ++index)
        {
            m_words[index].store(0, std::memory_order_relaxed);
        }
    }

    void Mark(uint64_t address, uint64_t size) noexcept
    {
        if (size == 0)
        {
            return;
        }

        uint64_t const moduleEnd = m_base + m_size;
        uint64_t const hitEnd =
            size > std::numeric_limits<uint64_t>::max() - address
                ? std::numeric_limits<uint64_t>::max()
                : address + size;
        uint64_t const start = std::max(address, m_base);
        uint64_t const end = std::min(hitEnd, moduleEnd);
        if (start >= end)
        {
            return;
        }

        m_callbackHits.fetch_add(1, std::memory_order_relaxed);
        uint64_t offset = start - m_base;
        uint64_t remaining = end - start;
        while (remaining != 0)
        {
            size_t const wordIndex = static_cast<size_t>(offset / 64);
            uint64_t const bitIndex = offset % 64;
            uint64_t const take = std::min<uint64_t>(remaining, 64 - bitIndex);
            uint64_t const mask =
                take == 64
                    ? std::numeric_limits<uint64_t>::max()
                    : ((uint64_t{1} << take) - 1) << bitIndex;
            m_words[wordIndex].fetch_or(mask, std::memory_order_relaxed);
            offset += take;
            remaining -= take;
        }
    }

    bool IsCovered(uint64_t rva) const noexcept
    {
        if (rva >= m_size)
        {
            return false;
        }
        size_t const wordIndex = static_cast<size_t>(rva / 64);
        uint64_t const bitIndex = rva % 64;
        return (m_words[wordIndex].load(std::memory_order_relaxed) &
                (uint64_t{1} << bitIndex)) != 0;
    }

    std::vector<Range> Ranges() const
    {
        std::vector<Range> result;
        bool inside = false;
        uint64_t start = 0;
        for (uint64_t rva = 0; rva < m_size; ++rva)
        {
            bool const covered = IsCovered(rva);
            if (covered && !inside)
            {
                start = rva;
                inside = true;
            }
            else if (!covered && inside)
            {
                result.push_back({start, rva});
                inside = false;
            }
        }
        if (inside)
        {
            result.push_back({start, m_size});
        }
        return CoalesceHalfOpenRanges(std::move(result));
    }

    uint64_t CallbackHits() const noexcept
    {
        return m_callbackHits.load(std::memory_order_relaxed);
    }

private:
    uint64_t m_base;
    uint64_t m_size;
    size_t m_wordCount;
    std::unique_ptr<std::atomic<uint64_t>[]> m_words;
    std::atomic<uint64_t> m_callbackHits = 0;
};

bool RunAtomicCoverageTests()
{
    auto fail =
        [](char const* group)
        {
            std::cerr << "atomic coverage self-test failed: " << group << "\n";
            return false;
        };

    {
        AtomicCoverage coverage(0x1000, 130);
        coverage.Mark(0x1000, 1);
        coverage.Mark(0x1081, 1);
        if (!coverage.IsCovered(0) ||
            !coverage.IsCovered(129) ||
            coverage.IsCovered(130))
        {
            return fail("first/last bit");
        }
    }
    {
        AtomicCoverage coverage(0x2000, 130);
        coverage.Mark(0x203F, 3);
        if (!coverage.IsCovered(63) ||
            !coverage.IsCovered(64) ||
            !coverage.IsCovered(65) ||
            coverage.IsCovered(62) ||
            coverage.IsCovered(66))
        {
            return fail("63/64 word boundary");
        }
    }
    {
        AtomicCoverage coverage(0x3000, 100);
        coverage.Mark(0x2FF0, 0x20);
        coverage.Mark(0x305F, 0x20);
        if (coverage.Ranges() !=
            std::vector<Range>{{0, 0x10}, {0x5F, 0x64}})
        {
            return fail("left/right clipping");
        }
    }
    {
        AtomicCoverage coverage(0x4000, 100);
        coverage.Mark(0x4010, 40);
        coverage.Mark(0x4020, 10);
        coverage.Mark(std::numeric_limits<uint64_t>::max() - 2, 10);
        if (coverage.Ranges() != std::vector<Range>{{0x10, 0x38}})
        {
            return fail("overlap and overflow saturation");
        }
    }
    {
        constexpr uint64_t base = 0x5000;
        constexpr uint64_t size = 257;
        AtomicCoverage coverage(base, size);
        std::vector<bool> reference(size, false);
        uint64_t state = 0x4D595DF4D0F33173ull;
        for (size_t iteration = 0; iteration < 1'000; ++iteration)
        {
            state = state * 6364136223846793005ull + 1442695040888963407ull;
            uint64_t const address = base - 32 + (state % (size + 64));
            state = state * 6364136223846793005ull + 1442695040888963407ull;
            uint64_t const length = state % 40;
            coverage.Mark(address, length);
            uint64_t const end =
                length > std::numeric_limits<uint64_t>::max() - address
                    ? std::numeric_limits<uint64_t>::max()
                    : address + length;
            uint64_t const clippedStart = std::max(address, base);
            uint64_t const clippedEnd = std::min(end, base + size);
            for (uint64_t cursor = clippedStart;
                 cursor < clippedEnd;
                 ++cursor)
            {
                reference[static_cast<size_t>(cursor - base)] = true;
            }
        }
        for (uint64_t rva = 0; rva < size; ++rva)
        {
            if (coverage.IsCovered(rva) != reference[static_cast<size_t>(rva)])
            {
                return fail("randomized scalar-reference parity");
            }
        }
    }
    {
        constexpr uint64_t size = 4096;
        constexpr size_t threadCount = 8;
        AtomicCoverage coverage(0x6000, size);
        std::array<std::thread, threadCount> workers;
        for (size_t worker = 0; worker < threadCount; ++worker)
        {
            workers[worker] = std::thread(
                [&coverage, worker]()
                {
                    for (uint64_t rva = worker; rva < size; rva += threadCount)
                    {
                        coverage.Mark(0x6000 + rva, 1);
                    }
                });
        }
        for (std::thread& worker : workers)
        {
            worker.join();
        }
        if (coverage.Ranges() != std::vector<Range>{{0, size}})
        {
            return fail("many-thread atomic OR");
        }
    }
    return true;
}

bool __fastcall ExecuteCallback(
    uintptr_t context,
    ICursorView::MemoryWatchpointResult const& watchpointResult,
    IThreadView const*)
{
    auto& coverage = *reinterpret_cast<AtomicCoverage*>(context);
    coverage.Mark(
        static_cast<uint64_t>(watchpointResult.Address),
        watchpointResult.Size);
    return false;
}

class GapStatistics
{
public:
    void Mark(GapKind kind, GapEventType event) noexcept
    {
        size_t const kindIndex = static_cast<size_t>(kind);
        size_t const eventIndex = static_cast<size_t>(event);
        if (kindIndex < m_kindCounts.size())
        {
            m_kindCounts[kindIndex].fetch_add(1, std::memory_order_relaxed);
        }
        if (eventIndex < m_eventCounts.size())
        {
            m_eventCounts[eventIndex].fetch_add(1, std::memory_order_relaxed);
        }
        m_total.fetch_add(1, std::memory_order_relaxed);
    }

    uint64_t Total() const noexcept
    {
        return m_total.load(std::memory_order_relaxed);
    }

    uint64_t KindCount(size_t index) const noexcept
    {
        return m_kindCounts[index].load(std::memory_order_relaxed);
    }

    uint64_t EventCount(size_t index) const noexcept
    {
        return m_eventCounts[index].load(std::memory_order_relaxed);
    }

private:
    std::array<std::atomic<uint64_t>, 4> m_kindCounts{};
    std::array<std::atomic<uint64_t>, 17> m_eventCounts{};
    std::atomic<uint64_t> m_total = 0;
};

bool __fastcall GapCallback(
    uintptr_t context,
    GapKind kind,
    GapEventType event,
    IThreadView const*)
{
    auto& statistics = *reinterpret_cast<GapStatistics*>(context);
    statistics.Mark(kind, event);
    return false;
}

constexpr size_t kNoIndex = std::numeric_limits<size_t>::max();

enum class CallContextEventKind
{
    Call,
    Entry,
    Return,
};

char const* GetCallContextEventKindName(CallContextEventKind kind) noexcept
{
    switch (kind)
    {
    case CallContextEventKind::Call: return "call";
    case CallContextEventKind::Entry: return "entry";
    case CallContextEventKind::Return: return "return";
    default: return "unknown";
    }
}

struct CallContextEvent
{
    CallContextEventKind Kind = CallContextEventKind::Call;
    size_t TargetIndex = kNoIndex;
    size_t InvocationIndex = kNoIndex;
    uint64_t AssociationEpoch = 0;
    Position PositionValue{};
    Position PreviousPosition{};
    uint32_t UniqueThreadId = 0;
    uint32_t ThreadId = 0;
    uint64_t ProgramCounter = 0;
    uint64_t StackPointer = 0;
    uint64_t FramePointer = 0;
    uint64_t InstructionTarget = 0;
    uint64_t FallThrough = 0;
    uint64_t BasicReturnValue = 0;
    uint32_t ContextFlags = 0;
    uint32_t Edi = 0;
    uint32_t Esi = 0;
    uint32_t Ebx = 0;
    uint32_t Edx = 0;
    uint32_t Ecx = 0;
    uint32_t Eax = 0;
    uint32_t Ebp = 0;
    uint32_t Eip = 0;
    uint32_t EFlags = 0;
    uint32_t Esp = 0;
    bool ControlRegistersValid = false;
    bool IntegerRegistersValid = false;
    bool RegisterViewsAgree = false;
    uint64_t StackMemoryAddress = 0;
    size_t StackMemorySize = 0;
    bool StackMemoryQueryValid = false;
    std::array<uint8_t, kMaxCallContextStackBytes> StackMemory{};
    uint64_t InstructionMemoryAddress = 0;
    size_t InstructionMemorySize = 0;
    bool InstructionMemoryQueryValid = false;
    std::array<uint8_t, 3> InstructionMemory{};
    bool DecodedNearReturn = false;
};

enum class CallContextInvocationGrade
{
    CallOnly,
    EntryOnly,
    CallEntry,
    CallEntryReturn,
};

char const* GetCallContextInvocationGradeName(
    CallContextInvocationGrade grade) noexcept
{
    switch (grade)
    {
    case CallContextInvocationGrade::CallOnly: return "CALL_ONLY";
    case CallContextInvocationGrade::EntryOnly: return "ENTRY_ONLY";
    case CallContextInvocationGrade::CallEntry: return "CALL_ENTRY";
    case CallContextInvocationGrade::CallEntryReturn:
        return "CALL_ENTRY_RETURN";
    default: return "UNKNOWN";
    }
}

struct CallContextInvocation
{
    size_t TargetIndex = kNoIndex;
    uint32_t UniqueThreadId = 0;
    uint64_t AssociationEpoch = 0;
    size_t CallEventIndex = kNoIndex;
    size_t EntryEventIndex = kNoIndex;
    size_t ReturnEventIndex = kNoIndex;
    CallContextInvocationGrade Grade = CallContextInvocationGrade::CallOnly;
    bool CallEntryChecksPassed = false;
    bool ReturnChecksPassed = false;
    bool GapCrossed = false;
    bool ContinuityBreakCrossed = false;
};

struct CallContextTargetCounts
{
    uint64_t Calls = 0;
    uint64_t Entries = 0;
    uint64_t Returns = 0;
};

struct AbsoluteTargetRange
{
    uint64_t Min = 0;
    uint64_t Max = 0;
    size_t TargetIndex = kNoIndex;
};

uint32_t ReadLittleEndianDword(
    std::array<uint8_t, kMaxCallContextStackBytes> const& bytes) noexcept
{
    return static_cast<uint32_t>(bytes[0]) |
           (static_cast<uint32_t>(bytes[1]) << 8) |
           (static_cast<uint32_t>(bytes[2]) << 16) |
           (static_cast<uint32_t>(bytes[3]) << 24);
}

bool PositionEquals(Position const& left, Position const& right) noexcept
{
    return left.Sequence == right.Sequence && left.Steps == right.Steps;
}

class CallContextRecorder
{
public:
    CallContextRecorder(
        uint64_t base,
        uint64_t moduleSize,
        std::vector<CallContextTarget> targets,
        uint64_t stackBytes,
        uint64_t eventLimit,
        GapStatistics& gapStatistics)
        : m_base(base),
          m_moduleSize(moduleSize),
          m_targets(std::move(targets)),
          m_stackBytes(static_cast<size_t>(stackBytes)),
          m_eventLimit(static_cast<size_t>(eventLimit)),
          m_gapStatistics(gapStatistics),
          m_targetCounts(m_targets.size())
    {
        m_events.reserve(m_eventLimit);
        m_invocations.reserve(m_eventLimit);
        for (size_t index = 0; index < m_targets.size(); ++index)
        {
            CallContextTarget const& target = m_targets[index];
            if (target.EntryRva >= m_moduleSize)
            {
                throw std::runtime_error(
                    "call-context entry lies outside the selected module");
            }
            uint64_t const absoluteEntry = m_base + target.EntryRva;
            if (!m_entries.emplace(absoluteEntry, index).second)
            {
                throw std::runtime_error(
                    "call-context target entries must be unique");
            }
            for (Range const& range : target.Ranges)
            {
                if (range.Max > m_moduleSize)
                {
                    throw std::runtime_error(
                        "call-context range lies outside the selected module");
                }
                m_ranges.push_back(
                    {m_base + range.Min, m_base + range.Max, index});
            }
        }
        std::sort(
            m_ranges.begin(),
            m_ranges.end(),
            [](AbsoluteTargetRange const& left, AbsoluteTargetRange const& right)
            {
                return left.Min < right.Min ||
                       (left.Min == right.Min && left.Max < right.Max);
            });
        for (size_t index = 1; index < m_ranges.size(); ++index)
        {
            if (m_ranges[index].Min < m_ranges[index - 1].Max)
            {
                throw std::runtime_error(
                    "selected call-context target ranges overlap; split the batch");
            }
        }
    }

    std::vector<CallContextTarget> const& Targets() const noexcept
    {
        return m_targets;
    }

    std::vector<CallContextTargetCounts> const& TargetCounts() const noexcept
    {
        return m_targetCounts;
    }

    std::vector<CallContextEvent> const& Events() const noexcept
    {
        return m_events;
    }

    std::vector<CallContextInvocation> const& Invocations() const noexcept
    {
        return m_invocations;
    }

    uint64_t CallReturnCallbacks() const noexcept
    {
        return m_callReturnCallbacks.load(std::memory_order_relaxed);
    }

    uint64_t EntryCallbacks() const noexcept
    {
        return m_entryCallbacks.load(std::memory_order_relaxed);
    }

    uint64_t ContinuityBreakCallbacks() const noexcept
    {
        return m_continuityBreakCallbacks.load(std::memory_order_relaxed);
    }

    uint64_t AssociationBarrierCount() const noexcept
    {
        return m_associationEpoch;
    }

    bool Truncated() const noexcept
    {
        return m_truncated.load(std::memory_order_relaxed);
    }

    bool CallbackFailed() const noexcept
    {
        return m_callbackFailed.load(std::memory_order_relaxed);
    }

    bool OrderingValid() const noexcept
    {
        return m_orderingValid;
    }

    bool ContextsValid() const noexcept
    {
        return m_contextsValid;
    }

    void MarkCallbackFailure() noexcept
    {
        m_callbackFailed.store(true, std::memory_order_relaxed);
    }

    void OnCallReturn(
        TTD::GuestAddress instructionTarget,
        TTD::GuestAddress fallThrough,
        IThreadView const* thread)
    {
        m_callReturnCallbacks.fetch_add(1, std::memory_order_relaxed);
        std::lock_guard<std::mutex> lock(m_mutex);
        uint64_t const absoluteTarget = static_cast<uint64_t>(instructionTarget);
        uint64_t const absoluteFallThrough = static_cast<uint64_t>(fallThrough);
        if (absoluteFallThrough != 0)
        {
            auto const found = m_entries.find(absoluteTarget);
            if (found == m_entries.end())
            {
                return;
            }
            size_t const targetIndex = found->second;
            ++m_targetCounts[targetIndex].Calls;
            size_t const eventIndex = CaptureEvent(
                CallContextEventKind::Call,
                targetIndex,
                absoluteTarget,
                absoluteFallThrough,
                thread);
            if (eventIndex == kNoIndex)
            {
                return;
            }
            CallContextEvent& event = m_events[eventIndex];
            CallContextInvocation invocation;
            invocation.TargetIndex = targetIndex;
            invocation.UniqueThreadId = event.UniqueThreadId;
            invocation.AssociationEpoch = event.AssociationEpoch;
            invocation.CallEventIndex = eventIndex;
            invocation.Grade = CallContextInvocationGrade::CallOnly;
            size_t const invocationIndex = m_invocations.size();
            m_invocations.push_back(invocation);
            event.InvocationIndex = invocationIndex;
            auto const pending = m_pendingByThread.find(event.UniqueThreadId);
            if (pending != m_pendingByThread.end())
            {
                m_invocations[pending->second].ContinuityBreakCrossed = true;
            }
            m_pendingByThread[event.UniqueThreadId] = invocationIndex;
            return;
        }

        uint64_t const programCounter =
            static_cast<uint64_t>(thread->GetProgramCounter());
        std::optional<size_t> const targetIndex = FindRangeTarget(programCounter);
        if (!targetIndex)
        {
            return;
        }
        ++m_targetCounts[*targetIndex].Returns;
        size_t const eventIndex = CaptureEvent(
            CallContextEventKind::Return,
            *targetIndex,
            absoluteTarget,
            0,
            thread);
        if (eventIndex != kNoIndex)
        {
            PairReturn(eventIndex);
        }
    }

    bool OnEntry(
        ICursorView::MemoryWatchpointResult const& watchpoint,
        IThreadView const* thread)
    {
        m_entryCallbacks.fetch_add(1, std::memory_order_relaxed);
        std::lock_guard<std::mutex> lock(m_mutex);
        uint64_t const programCounter =
            static_cast<uint64_t>(thread->GetProgramCounter());
        auto found = m_entries.find(programCounter);
        if (found == m_entries.end())
        {
            found = m_entries.find(static_cast<uint64_t>(watchpoint.Address));
        }
        if (found == m_entries.end())
        {
            m_contextsValid = false;
            return false;
        }
        size_t const targetIndex = found->second;
        if (programCounter != m_base + m_targets[targetIndex].EntryRva ||
            watchpoint.AccessType != DataAccessType::Execute)
        {
            m_contextsValid = false;
        }
        ++m_targetCounts[targetIndex].Entries;
        size_t const eventIndex = CaptureEvent(
            CallContextEventKind::Entry,
            targetIndex,
            m_base + m_targets[targetIndex].EntryRva,
            0,
            thread);
        if (eventIndex != kNoIndex)
        {
            PairEntry(eventIndex);
        }
        return false;
    }

    void OnGap(
        GapKind kind,
        GapEventType event,
        IThreadView const* thread) noexcept
    {
        m_gapStatistics.Mark(kind, event);
        if (!CallContextGapRequiresAssociationBarrier(kind))
        {
            return;
        }
        try
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            (void)thread;
            AdvanceAssociationEpoch(
                kind == GapKind::Unrecorded || kind == GapKind::Large,
                kind == GapKind::ContextSwitch);
        }
        catch (...)
        {
            MarkCallbackFailure();
        }
    }

    void OnContinuityBreak() noexcept
    {
        m_continuityBreakCallbacks.fetch_add(1, std::memory_order_relaxed);
        try
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            AdvanceAssociationEpoch(false, true);
        }
        catch (...)
        {
            MarkCallbackFailure();
        }
    }

private:
    void AdvanceAssociationEpoch(
        bool gapCrossed,
        bool continuityBreakCrossed)
    {
        if (m_associationEpoch == std::numeric_limits<uint64_t>::max())
        {
            throw std::runtime_error("call-context association epoch overflow");
        }
        for (auto const& [thread, invocationIndex] : m_pendingByThread)
        {
            (void)thread;
            CallContextInvocation& invocation = m_invocations[invocationIndex];
            invocation.GapCrossed = invocation.GapCrossed || gapCrossed;
            invocation.ContinuityBreakCrossed =
                invocation.ContinuityBreakCrossed || continuityBreakCrossed;
        }
        for (auto const& [thread, invocationIndexes] : m_activeByThread)
        {
            (void)thread;
            for (size_t const invocationIndex : invocationIndexes)
            {
                CallContextInvocation& invocation = m_invocations[invocationIndex];
                invocation.GapCrossed = invocation.GapCrossed || gapCrossed;
                invocation.ContinuityBreakCrossed =
                    invocation.ContinuityBreakCrossed || continuityBreakCrossed;
            }
        }
        m_pendingByThread.clear();
        m_activeByThread.clear();
        ++m_associationEpoch;
    }

    std::optional<size_t> FindRangeTarget(uint64_t address) const noexcept
    {
        auto const upper = std::upper_bound(
            m_ranges.begin(),
            m_ranges.end(),
            address,
            [](uint64_t value, AbsoluteTargetRange const& range)
            {
                return value < range.Min;
            });
        if (upper == m_ranges.begin())
        {
            return std::nullopt;
        }
        AbsoluteTargetRange const& candidate = *(upper - 1);
        if (address >= candidate.Min && address < candidate.Max)
        {
            return candidate.TargetIndex;
        }
        return std::nullopt;
    }

    size_t CaptureEvent(
        CallContextEventKind kind,
        size_t targetIndex,
        uint64_t instructionTarget,
        uint64_t fallThrough,
        IThreadView const* thread)
    {
        if (m_events.size() >= m_eventLimit)
        {
            m_truncated.store(true, std::memory_order_relaxed);
            return kNoIndex;
        }
        CallContextEvent event;
        event.Kind = kind;
        event.TargetIndex = targetIndex;
        event.AssociationEpoch = m_associationEpoch;
        event.PositionValue = thread->GetPosition();
        event.PreviousPosition = thread->GetPreviousPosition();
        ThreadInfo const& threadInfo = thread->GetThreadInfo();
        event.UniqueThreadId = static_cast<uint32_t>(threadInfo.UniqueId);
        event.ThreadId = static_cast<uint32_t>(threadInfo.Id);
        event.ProgramCounter =
            static_cast<uint64_t>(thread->GetProgramCounter());
        event.StackPointer = static_cast<uint64_t>(thread->GetStackPointer());
        event.FramePointer = static_cast<uint64_t>(thread->GetFramePointer());
        event.InstructionTarget = instructionTarget;
        event.FallThrough = fallThrough;
        event.BasicReturnValue = thread->GetBasicReturnValue();

        CROSS_PLATFORM_CONTEXT const raw = thread->GetCrossPlatformContext();
        X86_NT5_CONTEXT const& x86 = raw.X86Nt5Context;
        event.ContextFlags = x86.ContextFlags;
        event.Edi = x86.Edi;
        event.Esi = x86.Esi;
        event.Ebx = x86.Ebx;
        event.Edx = x86.Edx;
        event.Ecx = x86.Ecx;
        event.Eax = x86.Eax;
        event.Ebp = x86.Ebp;
        event.Eip = x86.Eip;
        event.EFlags = x86.EFlags;
        event.Esp = x86.Esp;
        event.ControlRegistersValid =
            (x86.ContextFlags & VDMCONTEXT_CONTROL) == VDMCONTEXT_CONTROL;
        event.IntegerRegistersValid =
            (x86.ContextFlags & VDMCONTEXT_INTEGER) == VDMCONTEXT_INTEGER;
        event.RegisterViewsAgree =
            event.ControlRegistersValid &&
            event.Eip == event.ProgramCounter &&
            event.Esp == event.StackPointer &&
            event.Ebp == event.FramePointer;

        uint64_t const requestedStackEnd =
            event.StackPointer + static_cast<uint64_t>(m_stackBytes);
        MemoryBuffer const stack = thread->QueryMemoryBuffer(
            static_cast<TTD::GuestAddress>(event.StackPointer),
            TTD::BufferView(event.StackMemory.data(), m_stackBytes));
        event.StackMemoryAddress = static_cast<uint64_t>(stack.Address);
        event.StackMemorySize = std::min(stack.Memory.Size, m_stackBytes);
        uintptr_t const hostStart = reinterpret_cast<uintptr_t>(
            event.StackMemory.data());
        uintptr_t const hostEnd = hostStart + m_stackBytes;
        uintptr_t const returnedHostStart = reinterpret_cast<uintptr_t>(
            stack.Memory.BaseAddress);
        bool const hostRangeValid =
            stack.Memory.Size == 0 ||
            (returnedHostStart >= hostStart &&
             returnedHostStart <= hostEnd &&
             stack.Memory.Size <= hostEnd - returnedHostStart);
        bool const guestRangeValid =
            event.StackMemoryAddress >= event.StackPointer &&
            event.StackMemoryAddress <= requestedStackEnd &&
            stack.Memory.Size <= requestedStackEnd - event.StackMemoryAddress;
        event.StackMemoryQueryValid =
            hostRangeValid && guestRangeValid;
        if (event.StackMemorySize != 0 &&
            stack.Memory.BaseAddress != event.StackMemory.data())
        {
            std::copy_n(
                static_cast<uint8_t const*>(stack.Memory.BaseAddress),
                event.StackMemorySize,
                event.StackMemory.begin());
        }

        if (kind == CallContextEventKind::Return)
        {
            MemoryBuffer const instruction = thread->QueryMemoryBuffer(
                static_cast<TTD::GuestAddress>(event.ProgramCounter),
                TTD::BufferView(
                    event.InstructionMemory.data(),
                    event.InstructionMemory.size()));
            event.InstructionMemoryAddress =
                static_cast<uint64_t>(instruction.Address);
            event.InstructionMemorySize = std::min(
                instruction.Memory.Size,
                event.InstructionMemory.size());
            uintptr_t const instructionHostStart = reinterpret_cast<uintptr_t>(
                event.InstructionMemory.data());
            uintptr_t const instructionHostEnd =
                instructionHostStart + event.InstructionMemory.size();
            uintptr_t const returnedInstructionHostStart =
                reinterpret_cast<uintptr_t>(instruction.Memory.BaseAddress);
            event.InstructionMemoryQueryValid =
                event.InstructionMemoryAddress >= event.ProgramCounter &&
                event.InstructionMemoryAddress <= event.ProgramCounter +
                    event.InstructionMemory.size() &&
                instruction.Memory.Size <= event.ProgramCounter +
                    event.InstructionMemory.size() -
                    event.InstructionMemoryAddress &&
                (instruction.Memory.Size == 0 ||
                 (returnedInstructionHostStart >= instructionHostStart &&
                  returnedInstructionHostStart <= instructionHostEnd &&
                  instruction.Memory.Size <=
                      instructionHostEnd - returnedInstructionHostStart));
            if (event.InstructionMemorySize != 0 &&
                instruction.Memory.BaseAddress != event.InstructionMemory.data())
            {
                std::copy_n(
                    static_cast<uint8_t const*>(instruction.Memory.BaseAddress),
                    event.InstructionMemorySize,
                    event.InstructionMemory.begin());
            }
            event.DecodedNearReturn =
                event.InstructionMemorySize >= 1 &&
                (event.InstructionMemory[0] == 0xC3 ||
                 (event.InstructionMemory[0] == 0xC2 &&
                  event.InstructionMemorySize >= 3));
        }

        bool const eventContextValid =
            event.ControlRegistersValid &&
            event.IntegerRegistersValid &&
            event.RegisterViewsAgree &&
            event.ProgramCounter <= std::numeric_limits<uint32_t>::max() &&
            event.StackPointer <= std::numeric_limits<uint32_t>::max() &&
            event.FramePointer <= std::numeric_limits<uint32_t>::max() &&
            event.StackMemoryQueryValid &&
            (kind != CallContextEventKind::Return ||
             event.InstructionMemoryQueryValid);
        m_contextsValid = m_contextsValid && eventContextValid;
        if (!m_events.empty() &&
            event.PositionValue < m_events.back().PositionValue)
        {
            m_orderingValid = false;
        }
        size_t const eventIndex = m_events.size();
        m_events.push_back(event);
        return eventIndex;
    }

    void PairEntry(size_t eventIndex)
    {
        CallContextEvent& entry = m_events[eventIndex];
        auto const pending = m_pendingByThread.find(entry.UniqueThreadId);
        bool paired = false;
        if (pending != m_pendingByThread.end())
        {
            size_t const invocationIndex = pending->second;
            CallContextInvocation& invocation = m_invocations[invocationIndex];
            CallContextEvent const& call = m_events[invocation.CallEventIndex];
            bool const stackHasReturnAddress =
                entry.StackMemoryQueryValid &&
                entry.StackMemoryAddress == entry.StackPointer &&
                entry.StackMemorySize >= 4;
            bool const callStackHasReturnAddress =
                call.StackMemoryQueryValid &&
                call.StackMemoryAddress == call.StackPointer &&
                call.StackMemorySize >= 4;
            bool const registersUnchanged =
                call.IntegerRegistersValid && entry.IntegerRegistersValid &&
                call.ControlRegistersValid && entry.ControlRegistersValid &&
                call.Edi == entry.Edi && call.Esi == entry.Esi &&
                call.Ebx == entry.Ebx && call.Edx == entry.Edx &&
                call.Ecx == entry.Ecx && call.Eax == entry.Eax &&
                call.Ebp == entry.Ebp && call.EFlags == entry.EFlags;
            paired =
                invocation.TargetIndex == entry.TargetIndex &&
                invocation.AssociationEpoch == entry.AssociationEpoch &&
                !invocation.GapCrossed &&
                !invocation.ContinuityBreakCrossed &&
                PositionEquals(entry.PreviousPosition, call.PositionValue) &&
                entry.StackPointer == call.StackPointer &&
                callStackHasReturnAddress &&
                stackHasReturnAddress &&
                ReadLittleEndianDword(call.StackMemory) == call.FallThrough &&
                ReadLittleEndianDword(entry.StackMemory) == call.FallThrough &&
                registersUnchanged;
            if (paired)
            {
                invocation.EntryEventIndex = eventIndex;
                invocation.Grade = CallContextInvocationGrade::CallEntry;
                invocation.CallEntryChecksPassed = true;
                entry.InvocationIndex = invocationIndex;
                m_activeByThread[entry.UniqueThreadId].push_back(invocationIndex);
            }
            m_pendingByThread.erase(pending);
        }
        if (!paired)
        {
            CallContextInvocation invocation;
            invocation.TargetIndex = entry.TargetIndex;
            invocation.UniqueThreadId = entry.UniqueThreadId;
            invocation.AssociationEpoch = entry.AssociationEpoch;
            invocation.EntryEventIndex = eventIndex;
            invocation.Grade = CallContextInvocationGrade::EntryOnly;
            size_t const invocationIndex = m_invocations.size();
            m_invocations.push_back(invocation);
            entry.InvocationIndex = invocationIndex;
        }
    }

    void PairReturn(size_t eventIndex)
    {
        CallContextEvent& returned = m_events[eventIndex];
        auto active = m_activeByThread.find(returned.UniqueThreadId);
        if (active == m_activeByThread.end() || active->second.empty())
        {
            return;
        }
        size_t const invocationIndex = active->second.back();
        active->second.pop_back();
        if (active->second.empty())
        {
            m_activeByThread.erase(active);
        }
        CallContextInvocation& invocation = m_invocations[invocationIndex];
        if (invocation.TargetIndex != returned.TargetIndex)
        {
            invocation.ContinuityBreakCrossed = true;
            return;
        }
        CallContextEvent const& call = m_events[invocation.CallEventIndex];
        CallContextEvent const& entry = m_events[invocation.EntryEventIndex];
        bool const stackHasReturnAddress =
            returned.StackMemoryQueryValid &&
            returned.StackMemoryAddress == returned.StackPointer &&
            returned.StackMemorySize >= 4;
        bool const checksPassed =
            !invocation.GapCrossed &&
            !invocation.ContinuityBreakCrossed &&
            invocation.AssociationEpoch == returned.AssociationEpoch &&
            returned.DecodedNearReturn &&
            returned.InstructionMemoryAddress == returned.ProgramCounter &&
            returned.StackPointer == entry.StackPointer &&
            stackHasReturnAddress &&
            ReadLittleEndianDword(returned.StackMemory) ==
                returned.InstructionTarget &&
            returned.InstructionTarget == call.FallThrough;
        if (!checksPassed)
        {
            return;
        }
        invocation.ReturnEventIndex = eventIndex;
        invocation.ReturnChecksPassed = true;
        returned.InvocationIndex = invocationIndex;
        invocation.Grade = CallContextInvocationGrade::CallEntryReturn;
    }

    uint64_t m_base;
    uint64_t m_moduleSize;
    std::vector<CallContextTarget> m_targets;
    size_t m_stackBytes;
    size_t m_eventLimit;
    GapStatistics& m_gapStatistics;
    std::vector<CallContextTargetCounts> m_targetCounts;
    std::unordered_map<uint64_t, size_t> m_entries;
    std::vector<AbsoluteTargetRange> m_ranges;
    std::vector<CallContextEvent> m_events;
    std::vector<CallContextInvocation> m_invocations;
    std::unordered_map<uint32_t, size_t> m_pendingByThread;
    std::unordered_map<uint32_t, std::vector<size_t>> m_activeByThread;
    std::atomic<uint64_t> m_callReturnCallbacks = 0;
    std::atomic<uint64_t> m_entryCallbacks = 0;
    std::atomic<uint64_t> m_continuityBreakCallbacks = 0;
    std::atomic<bool> m_truncated = false;
    std::atomic<bool> m_callbackFailed = false;
    bool m_orderingValid = true;
    bool m_contextsValid = true;
    uint64_t m_associationEpoch = 0;
    std::mutex m_mutex;
};

void __fastcall CallContextCallReturnCallback(
    uintptr_t context,
    TTD::GuestAddress instructionTarget,
    TTD::GuestAddress fallThrough,
    IThreadView const* thread)
{
    auto& recorder = *reinterpret_cast<CallContextRecorder*>(context);
    try
    {
        recorder.OnCallReturn(instructionTarget, fallThrough, thread);
    }
    catch (...)
    {
        recorder.MarkCallbackFailure();
    }
}

bool __fastcall CallContextEntryCallback(
    uintptr_t context,
    ICursorView::MemoryWatchpointResult const& watchpoint,
    IThreadView const* thread)
{
    auto& recorder = *reinterpret_cast<CallContextRecorder*>(context);
    try
    {
        return recorder.OnEntry(watchpoint, thread);
    }
    catch (...)
    {
        recorder.MarkCallbackFailure();
        return false;
    }
}

bool __fastcall CallContextGapCallback(
    uintptr_t context,
    GapKind kind,
    GapEventType event,
    IThreadView const* thread)
{
    auto& recorder = *reinterpret_cast<CallContextRecorder*>(context);
    recorder.OnGap(kind, event, thread);
    return false;
}

void __fastcall CallContextContinuityBreakCallback(uintptr_t context)
{
    auto& recorder = *reinterpret_cast<CallContextRecorder*>(context);
    recorder.OnContinuityBreak();
}

struct DataWriteMemoryImage
{
    uint64_t Address = 0;
    size_t Size = 0;
    size_t RangeCount = 0;
    Position ObservationPosition{};
    uint64_t SourceSequence = 0;
    bool SingleRange = false;
    bool QueryValid = false;
    std::array<uint8_t, kMaxDataWriteBytes> Bytes{};
};

bool DataWriteMemorySourceSequenceMatches(
    DataWriteMemoryImage const& image) noexcept;

template <typename QueryOwner>
DataWriteMemoryImage QueryExactDataWriteMemory(
    QueryOwner const& owner,
    DataWriteTarget const& target)
{
    DataWriteMemoryImage image;
    image.Address = target.Address;
    image.ObservationPosition = owner.GetPosition();
    std::fill(image.Bytes.begin(), image.Bytes.end(), uint8_t{0});
    MemoryRange range{};
    MemoryBufferWithRanges const memory = owner.QueryMemoryBufferWithRanges(
        static_cast<TTD::GuestAddress>(target.Address),
        TTD::BufferView(image.Bytes.data(), static_cast<size_t>(target.Size)),
        1,
        &range);
    image.Address = static_cast<uint64_t>(memory.Address);
    image.Size = std::min(memory.Memory.Size, static_cast<size_t>(target.Size));
    image.RangeCount = memory.RangeCount;
    image.SingleRange =
        memory.RangeCount == 1 &&
        range.Address == static_cast<TTD::GuestAddress>(target.Address) &&
        range.Memory.Size == target.Size;
    if (image.SingleRange)
    {
        image.SourceSequence = static_cast<uint64_t>(range.Sequence);
    }
    uintptr_t const hostStart =
        reinterpret_cast<uintptr_t>(image.Bytes.data());
    uintptr_t const hostEnd = hostStart + static_cast<size_t>(target.Size);
    uintptr_t const returnedHostStart =
        reinterpret_cast<uintptr_t>(memory.Memory.BaseAddress);
    bool const hostRangeValid =
        returnedHostStart >= hostStart && returnedHostStart <= hostEnd &&
        memory.Memory.Size <= hostEnd - returnedHostStart;
    uintptr_t const returnedRangeHostStart =
        reinterpret_cast<uintptr_t>(range.Memory.BaseAddress);
    bool const rangeHostValid =
        image.SingleRange && returnedRangeHostStart >= hostStart &&
        returnedRangeHostStart <= hostEnd &&
        range.Memory.Size <= hostEnd - returnedRangeHostStart;
    image.QueryValid =
        memory.Address == static_cast<TTD::GuestAddress>(target.Address) &&
        memory.Memory.Size == target.Size && hostRangeValid && rangeHostValid;
    if (image.Size != 0 && memory.Memory.BaseAddress != image.Bytes.data() &&
        hostRangeValid)
    {
        std::copy_n(
            static_cast<uint8_t const*>(memory.Memory.BaseAddress),
            image.Size,
            image.Bytes.begin());
    }
    return image;
}

struct DataWriteEvent
{
    size_t TargetIndex = kNoIndex;
    size_t PairIndex = kNoIndex;
    size_t IntersectingTargetCount = 0;
    uint64_t ContinuityEpoch = 0;
    DataAccessType AccessType = DataAccessType::Write;
    uint64_t AccessAddress = 0;
    uint64_t AccessSize = 0;
    Position PositionValue{};
    Position PreviousPosition{};
    uint32_t UniqueThreadId = 0;
    uint32_t ThreadId = 0;
    uint64_t ProgramCounter = 0;
    uint64_t StackPointer = 0;
    uint64_t FramePointer = 0;
    uint32_t ContextFlags = 0;
    uint32_t Edi = 0;
    uint32_t Esi = 0;
    uint32_t Ebx = 0;
    uint32_t Edx = 0;
    uint32_t Ecx = 0;
    uint32_t Eax = 0;
    uint32_t Ebp = 0;
    uint32_t Eip = 0;
    uint32_t EFlags = 0;
    uint32_t Esp = 0;
    bool ControlRegistersValid = false;
    bool IntegerRegistersValid = false;
    bool RegisterViewsAgree = false;
    DataWriteMemoryImage ObservedMemory;
};

struct DataWritePair
{
    size_t TargetIndex = kNoIndex;
    size_t OverwriteEventIndex = kNoIndex;
    size_t WriteEventIndex = kNoIndex;
    uint64_t ContinuityEpoch = 0;
    bool ChecksPassed = false;
    bool Changed = false;
};

struct PendingDataWrite
{
    size_t EventIndex = kNoIndex;
};

struct DataWriteTargetCounts
{
    uint64_t Overwrites = 0;
    uint64_t Writes = 0;
};

class DataWriteRecorder
{
public:
    DataWriteRecorder(
        std::vector<DataWriteTarget> targets,
        uint64_t eventLimit,
        GapStatistics& gapStatistics)
        : m_targets(std::move(targets)),
          m_eventLimit(static_cast<size_t>(eventLimit)),
          m_gapStatistics(gapStatistics),
          m_targetCounts(m_targets.size())
    {
        m_events.reserve(m_eventLimit);
    }

    std::vector<DataWriteTarget> const& Targets() const noexcept
    {
        return m_targets;
    }

    std::vector<DataWriteTargetCounts> const& TargetCounts() const noexcept
    {
        return m_targetCounts;
    }

    std::vector<DataWriteEvent> const& Events() const noexcept
    {
        return m_events;
    }

    std::vector<DataWritePair> const& Pairs() const noexcept
    {
        return m_pairs;
    }

    uint64_t CallbackHits() const noexcept
    {
        return m_callbackHits.load(std::memory_order_relaxed);
    }

    uint64_t AmbiguousCallbacks() const noexcept
    {
        return m_ambiguousCallbacks.load(std::memory_order_relaxed);
    }

    uint64_t NontrivialGapCount() const noexcept
    {
        return m_nontrivialGapCount.load(std::memory_order_relaxed);
    }

    uint64_t ContinuityBreakCount() const noexcept
    {
        return m_continuityBreakCount.load(std::memory_order_relaxed);
    }

    bool Truncated() const noexcept
    {
        return m_truncated.load(std::memory_order_relaxed);
    }

    bool CallbackFailed() const noexcept
    {
        return m_callbackFailed.load(std::memory_order_relaxed);
    }

    bool OrderingValid() const noexcept
    {
        return m_orderingValid;
    }

    bool ContextsValid() const noexcept
    {
        return m_contextsValid;
    }

    bool PairingValid() const noexcept
    {
        return m_pairingValid;
    }

    bool PairingComplete() const noexcept
    {
        return m_pairs.size() <= m_events.size() / 2 &&
            m_pairs.size() * 2 == m_events.size();
    }

    void MarkCallbackFailure() noexcept
    {
        m_callbackFailed.store(true, std::memory_order_relaxed);
    }

    bool OnMemory(
        ICursorView::MemoryWatchpointResult const& watchpoint,
        IThreadView const* thread)
    {
        m_callbackHits.fetch_add(1, std::memory_order_relaxed);
        std::lock_guard<std::mutex> lock(m_mutex);
        if (m_events.size() >= m_eventLimit)
        {
            m_truncated.store(true, std::memory_order_relaxed);
            return false;
        }

        DataWriteEvent event;
        event.ContinuityEpoch = m_continuityEpoch;
        event.AccessType = watchpoint.AccessType;
        event.AccessAddress = static_cast<uint64_t>(watchpoint.Address);
        event.AccessSize = watchpoint.Size;
        std::vector<size_t> const intersections = FindDataWriteIntersections(
            m_targets,
            event.AccessAddress,
            event.AccessSize);
        event.IntersectingTargetCount = intersections.size();
        if (intersections.size() == 1)
        {
            event.TargetIndex = intersections.front();
        }
        else
        {
            m_ambiguousCallbacks.fetch_add(1, std::memory_order_relaxed);
        }

        event.PositionValue = thread->GetPosition();
        event.PreviousPosition = thread->GetPreviousPosition();
        ThreadInfo const& threadInfo = thread->GetThreadInfo();
        event.UniqueThreadId = static_cast<uint32_t>(threadInfo.UniqueId);
        event.ThreadId = static_cast<uint32_t>(threadInfo.Id);
        event.ProgramCounter =
            static_cast<uint64_t>(thread->GetProgramCounter());
        event.StackPointer = static_cast<uint64_t>(thread->GetStackPointer());
        event.FramePointer = static_cast<uint64_t>(thread->GetFramePointer());

        CROSS_PLATFORM_CONTEXT const raw = thread->GetCrossPlatformContext();
        X86_NT5_CONTEXT const& x86 = raw.X86Nt5Context;
        event.ContextFlags = x86.ContextFlags;
        event.Edi = x86.Edi;
        event.Esi = x86.Esi;
        event.Ebx = x86.Ebx;
        event.Edx = x86.Edx;
        event.Ecx = x86.Ecx;
        event.Eax = x86.Eax;
        event.Ebp = x86.Ebp;
        event.Eip = x86.Eip;
        event.EFlags = x86.EFlags;
        event.Esp = x86.Esp;
        event.ControlRegistersValid =
            (x86.ContextFlags & VDMCONTEXT_CONTROL) == VDMCONTEXT_CONTROL;
        event.IntegerRegistersValid =
            (x86.ContextFlags & VDMCONTEXT_INTEGER) == VDMCONTEXT_INTEGER;
        event.RegisterViewsAgree =
            event.ControlRegistersValid &&
            event.Eip == event.ProgramCounter &&
            event.Esp == event.StackPointer &&
            event.Ebp == event.FramePointer;

        if (event.TargetIndex != kNoIndex)
        {
            event.ObservedMemory = QueryExactDataWriteMemory(
                *thread,
                m_targets[event.TargetIndex]);
            DataWriteTargetCounts& counts = m_targetCounts[event.TargetIndex];
            if (event.AccessType == DataAccessType::Overwrite)
            {
                ++counts.Overwrites;
            }
            else if (event.AccessType == DataAccessType::Write)
            {
                ++counts.Writes;
            }
        }

        constexpr uint64_t x86AddressSpace = uint64_t{1} << 32;
        bool const accessRangeValid =
            event.AccessSize != 0 &&
            event.AccessAddress < x86AddressSpace &&
            event.AccessSize <= x86AddressSpace - event.AccessAddress;
        bool const eventContextValid =
            event.IntersectingTargetCount == 1 &&
            (event.AccessType == DataAccessType::Overwrite ||
             event.AccessType == DataAccessType::Write) &&
            accessRangeValid &&
            event.ControlRegistersValid &&
            event.IntegerRegistersValid &&
            event.RegisterViewsAgree &&
            event.ProgramCounter < x86AddressSpace &&
            event.StackPointer < x86AddressSpace &&
            event.FramePointer < x86AddressSpace &&
            event.ObservedMemory.QueryValid &&
            DataWriteMemorySourceSequenceMatches(event.ObservedMemory) &&
            PositionEquals(
                event.ObservedMemory.ObservationPosition,
                event.PositionValue) &&
            event.PreviousPosition < event.PositionValue;
        m_contextsValid = m_contextsValid && eventContextValid;
        if (!m_events.empty() &&
            event.PositionValue < m_events.back().PositionValue)
        {
            m_orderingValid = false;
        }
        size_t const eventIndex = m_events.size();
        m_events.push_back(event);
        PairEvent(eventIndex);
        return false;
    }

    void OnGap(GapKind kind, GapEventType event) noexcept
    {
        m_gapStatistics.Mark(kind, event);
        if (kind != GapKind::NoGap)
        {
            m_nontrivialGapCount.fetch_add(1, std::memory_order_relaxed);
            try
            {
                std::lock_guard<std::mutex> lock(m_mutex);
                ++m_continuityEpoch;
                m_pending.clear();
            }
            catch (...)
            {
                MarkCallbackFailure();
            }
        }
    }

    void OnContinuityBreak() noexcept
    {
        m_continuityBreakCount.fetch_add(1, std::memory_order_relaxed);
        try
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            ++m_continuityEpoch;
            m_pending.clear();
        }
        catch (...)
        {
            MarkCallbackFailure();
        }
    }

private:
    static bool SameWriteBoundary(
        DataWriteEvent const& overwrite,
        DataWriteEvent const& written) noexcept
    {
        return
            overwrite.TargetIndex == written.TargetIndex &&
            overwrite.ContinuityEpoch == written.ContinuityEpoch &&
            overwrite.UniqueThreadId == written.UniqueThreadId &&
            overwrite.ProgramCounter == written.ProgramCounter &&
            overwrite.StackPointer == written.StackPointer &&
            overwrite.FramePointer == written.FramePointer &&
            overwrite.AccessAddress == written.AccessAddress &&
            overwrite.AccessSize == written.AccessSize &&
            PositionEquals(overwrite.PositionValue, written.PositionValue) &&
            PositionEquals(overwrite.PreviousPosition, written.PreviousPosition) &&
            overwrite.ContextFlags == written.ContextFlags &&
            overwrite.Edi == written.Edi && overwrite.Esi == written.Esi &&
            overwrite.Ebx == written.Ebx && overwrite.Edx == written.Edx &&
            overwrite.Ecx == written.Ecx && overwrite.Eax == written.Eax &&
            overwrite.Ebp == written.Ebp && overwrite.Eip == written.Eip &&
            overwrite.EFlags == written.EFlags && overwrite.Esp == written.Esp;
    }

    void PairEvent(size_t eventIndex)
    {
        DataWriteEvent& event = m_events[eventIndex];
        if (event.TargetIndex == kNoIndex)
        {
            return;
        }
        if (event.AccessType == DataAccessType::Overwrite)
        {
            for (PendingDataWrite const& pending : m_pending)
            {
                if (SameWriteBoundary(m_events[pending.EventIndex], event))
                {
                    m_pairingValid = false;
                }
            }
            m_pending.push_back({eventIndex});
            return;
        }
        if (event.AccessType != DataAccessType::Write)
        {
            m_pairingValid = false;
            return;
        }

        size_t matchCount = 0;
        size_t matchOffset = kNoIndex;
        for (size_t index = 0; index < m_pending.size(); ++index)
        {
            DataWriteEvent const& overwrite =
                m_events[m_pending[index].EventIndex];
            if (SameWriteBoundary(overwrite, event))
            {
                ++matchCount;
                matchOffset = index;
            }
        }
        if (matchCount != 1)
        {
            if (matchCount > 1)
            {
                m_pairingValid = false;
            }
            return;
        }

        size_t const overwriteEventIndex = m_pending[matchOffset].EventIndex;
        DataWriteEvent& overwrite = m_events[overwriteEventIndex];
        DataWriteTarget const& target = m_targets[event.TargetIndex];
        bool const changed = !std::equal(
            overwrite.ObservedMemory.Bytes.begin(),
            overwrite.ObservedMemory.Bytes.begin() +
                static_cast<size_t>(target.Size),
            event.ObservedMemory.Bytes.begin());
        size_t const pairIndex = m_pairs.size();
        m_pairs.push_back(
            DataWritePair{
                .TargetIndex = event.TargetIndex,
                .OverwriteEventIndex = overwriteEventIndex,
                .WriteEventIndex = eventIndex,
                .ContinuityEpoch = event.ContinuityEpoch,
                .ChecksPassed = true,
                .Changed = changed,
            });
        overwrite.PairIndex = pairIndex;
        event.PairIndex = pairIndex;
        m_pending.erase(m_pending.begin() + matchOffset);
    }

    std::vector<DataWriteTarget> m_targets;
    size_t m_eventLimit;
    GapStatistics& m_gapStatistics;
    std::vector<DataWriteTargetCounts> m_targetCounts;
    std::vector<DataWriteEvent> m_events;
    std::vector<DataWritePair> m_pairs;
    std::vector<PendingDataWrite> m_pending;
    std::atomic<uint64_t> m_callbackHits = 0;
    std::atomic<uint64_t> m_ambiguousCallbacks = 0;
    std::atomic<uint64_t> m_nontrivialGapCount = 0;
    std::atomic<uint64_t> m_continuityBreakCount = 0;
    std::atomic<bool> m_truncated = false;
    std::atomic<bool> m_callbackFailed = false;
    bool m_orderingValid = true;
    bool m_contextsValid = true;
    bool m_pairingValid = true;
    uint64_t m_continuityEpoch = 0;
    std::mutex m_mutex;
};

bool __fastcall DataWriteMemoryCallback(
    uintptr_t context,
    ICursorView::MemoryWatchpointResult const& watchpoint,
    IThreadView const* thread)
{
    auto& recorder = *reinterpret_cast<DataWriteRecorder*>(context);
    try
    {
        return recorder.OnMemory(watchpoint, thread);
    }
    catch (...)
    {
        recorder.MarkCallbackFailure();
        return false;
    }
}

bool __fastcall DataWriteGapCallback(
    uintptr_t context,
    GapKind kind,
    GapEventType event,
    IThreadView const*)
{
    auto& recorder = *reinterpret_cast<DataWriteRecorder*>(context);
    recorder.OnGap(kind, event);
    return false;
}

void __fastcall DataWriteContinuityBreakCallback(uintptr_t context)
{
    auto& recorder = *reinterpret_cast<DataWriteRecorder*>(context);
    recorder.OnContinuityBreak();
}

bool DataWriteMemorySourceSequenceMatches(
    DataWriteMemoryImage const& image) noexcept
{
    return image.SourceSequence ==
        static_cast<uint64_t>(image.ObservationPosition.Sequence);
}

bool DataWriteMemoryBytesEqual(
    DataWriteMemoryImage const& left,
    DataWriteMemoryImage const& right,
    size_t size) noexcept
{
    return left.QueryValid && right.QueryValid &&
        size <= left.Bytes.size() && size <= right.Bytes.size() &&
        std::equal(
            left.Bytes.begin(),
            left.Bytes.begin() + size,
            right.Bytes.begin());
}

struct DataWriteTargetEvidence
{
    char const* Grade = "BLOCKED";
    bool InitialSequenceMatched = false;
    bool FinalSequenceMatched = false;
    bool EventMemorySequenceSourced = false;
    bool ChainClosed = false;
    bool Passed = false;
};

DataWriteTargetEvidence EvaluateDataWriteTargetEvidence(
    size_t targetIndex,
    std::vector<DataWriteTarget> const& targets,
    std::vector<DataWriteTargetCounts> const& counts,
    std::vector<DataWriteEvent> const& events,
    std::vector<DataWritePair> const& pairs,
    std::vector<DataWriteMemoryImage> const& initialImages,
    std::vector<DataWriteMemoryImage> const& finalImages)
{
    DataWriteTargetEvidence result;
    if (targetIndex >= targets.size() || targetIndex >= counts.size() ||
        targetIndex >= initialImages.size() ||
        targetIndex >= finalImages.size())
    {
        return result;
    }

    DataWriteTarget const& target = targets[targetIndex];
    DataWriteTargetCounts const& observed = counts[targetIndex];
    DataWriteMemoryImage const& initial = initialImages[targetIndex];
    DataWriteMemoryImage const& final = finalImages[targetIndex];
    result.InitialSequenceMatched =
        DataWriteMemorySourceSequenceMatches(initial);
    result.FinalSequenceMatched =
        DataWriteMemorySourceSequenceMatches(final);
    if (!target.ExpectedOverwriteCount || !target.ExpectedWriteCount)
    {
        result.Grade = "DISCOVERY_ONLY";
        return result;
    }
    if (*target.ExpectedOverwriteCount != *target.ExpectedWriteCount)
    {
        return result;
    }

    std::vector<DataWritePair const*> targetPairs;
    size_t targetEventCount = 0;
    for (DataWriteEvent const& event : events)
    {
        if (event.TargetIndex == targetIndex)
        {
            ++targetEventCount;
        }
    }
    for (DataWritePair const& pair : pairs)
    {
        if (pair.TargetIndex == targetIndex)
        {
            targetPairs.push_back(&pair);
        }
    }
    uint64_t const expected = *target.ExpectedWriteCount;
    if (expected == 0)
    {
        result.ChainClosed =
            observed.Overwrites == 0 && observed.Writes == 0 &&
            targetEventCount == 0 && targetPairs.empty();
        result.Passed = result.ChainClosed;
        if (result.Passed)
        {
            result.Grade = "NO_WRITE_CALLBACK_WITNESS";
        }
        return result;
    }

    if (observed.Overwrites != expected || observed.Writes != expected ||
        targetPairs.size() != expected || targetEventCount != expected * 2)
    {
        return result;
    }
    DataWriteMemoryImage const* cursor = nullptr;
    size_t previousWriteEvent = kNoIndex;
    result.EventMemorySequenceSourced = true;
    for (DataWritePair const* pair : targetPairs)
    {
        if (pair == nullptr || !pair->ChecksPassed ||
            pair->OverwriteEventIndex >= events.size() ||
            pair->WriteEventIndex >= events.size() ||
            pair->OverwriteEventIndex >= pair->WriteEventIndex ||
            (previousWriteEvent != kNoIndex &&
             pair->OverwriteEventIndex <= previousWriteEvent))
        {
            return result;
        }
        DataWriteEvent const& overwrite = events[pair->OverwriteEventIndex];
        DataWriteEvent const& written = events[pair->WriteEventIndex];
        if (overwrite.TargetIndex != targetIndex ||
            written.TargetIndex != targetIndex ||
            overwrite.AccessType != DataAccessType::Overwrite ||
            written.AccessType != DataAccessType::Write)
        {
            return result;
        }
        bool const eventMemorySourced =
            overwrite.ObservedMemory.QueryValid &&
            written.ObservedMemory.QueryValid &&
            DataWriteMemorySourceSequenceMatches(overwrite.ObservedMemory) &&
            DataWriteMemorySourceSequenceMatches(written.ObservedMemory) &&
            PositionEquals(
                overwrite.ObservedMemory.ObservationPosition,
                overwrite.PositionValue) &&
            PositionEquals(
                written.ObservedMemory.ObservationPosition,
                written.PositionValue);
        result.EventMemorySequenceSourced =
            result.EventMemorySequenceSourced && eventMemorySourced;
        if (!eventMemorySourced ||
            (cursor != nullptr &&
             !DataWriteMemoryBytesEqual(
                 *cursor,
                 overwrite.ObservedMemory,
                 static_cast<size_t>(target.Size))))
        {
            return result;
        }
        cursor = &written.ObservedMemory;
        previousWriteEvent = pair->WriteEventIndex;
    }
    result.ChainClosed = cursor != nullptr && result.EventMemorySequenceSourced;
    result.Passed = result.ChainClosed;
    if (result.Passed)
    {
        result.Grade = "WATCHPOINT_CHAIN_CLOSED";
    }
    return result;
}

bool RunDataWriteEvidenceTests()
{
    Position const position{
        static_cast<TTD::SequenceId>(0x10),
        static_cast<StepCount>(0x20),
    };
    auto image =
        [&position](uint8_t value, uint64_t sourceSequence)
        {
            DataWriteMemoryImage result;
            result.Address = 0x1000;
            result.Size = 4;
            result.RangeCount = 1;
            result.ObservationPosition = position;
            result.SourceSequence = sourceSequence;
            result.SingleRange = true;
            result.QueryValid = true;
            result.Bytes[0] = value;
            return result;
        };
    std::vector<DataWriteTarget> const targets{
        {
            .Address = 0x1000,
            .Size = 4,
            .ExpectedOverwriteCount = 1,
            .ExpectedWriteCount = 1,
        },
    };

    std::vector<DataWriteMemoryImage> initial{
        image(0x11, 0x0F),
    };
    std::vector<DataWriteMemoryImage> final{
        image(0x22, 0x10),
    };
    std::vector<DataWriteEvent> events(2);
    events[0].TargetIndex = 0;
    events[0].AccessType = DataAccessType::Overwrite;
    events[0].PositionValue = position;
    events[0].ObservedMemory = image(0x11, 0x10);
    events[1].TargetIndex = 0;
    events[1].AccessType = DataAccessType::Write;
    events[1].PositionValue = position;
    events[1].ObservedMemory = image(0x22, 0x10);
    std::vector<DataWritePair> const pairs{
        {
            .TargetIndex = 0,
            .OverwriteEventIndex = 0,
            .WriteEventIndex = 1,
            .ChecksPassed = true,
            .Changed = true,
        },
    };
    std::vector<DataWriteTargetCounts> const oneWrite{
        {.Overwrites = 1, .Writes = 1},
    };
    DataWriteTargetEvidence const closedWrite =
        EvaluateDataWriteTargetEvidence(
            0, targets, oneWrite, events, pairs, initial, final);
    if (!closedWrite.Passed || !closedWrite.ChainClosed ||
        !closedWrite.EventMemorySequenceSourced ||
        std::string_view(closedWrite.Grade) != "WATCHPOINT_CHAIN_CLOSED")
    {
        std::cerr << "data-write evidence self-test failed: anchored write\n";
        return false;
    }

    final[0].SourceSequence = 0x0F;
    if (!EvaluateDataWriteTargetEvidence(
             0, targets, oneWrite, events, pairs, initial, final).Passed)
    {
        std::cerr
            << "data-write evidence self-test failed: endpoint-independent write\n";
        return false;
    }
    events[0].ObservedMemory.SourceSequence = 0x0F;
    if (EvaluateDataWriteTargetEvidence(
            0, targets, oneWrite, events, pairs, initial, final).Passed)
    {
        std::cerr << "data-write evidence self-test failed: unsourced event\n";
        return false;
    }
    events[0].ObservedMemory.SourceSequence = 0x10;

    initial[0] = image(0x33, 0x10);
    final[0] = image(0x34, 0x0F);
    std::vector<DataWriteTarget> const zeroTargets{
        {
            .Address = 0x1000,
            .Size = 4,
            .ExpectedOverwriteCount = 0,
            .ExpectedWriteCount = 0,
        },
    };
    std::vector<DataWriteTargetCounts> const zeroWrites(1);
    DataWriteTargetEvidence const noWrite =
        EvaluateDataWriteTargetEvidence(
            0, zeroTargets, zeroWrites, {}, {}, initial, final);
    if (!noWrite.Passed || !noWrite.ChainClosed ||
        std::string_view(noWrite.Grade) != "NO_WRITE_CALLBACK_WITNESS")
    {
        std::cerr << "data-write evidence self-test failed: zero write\n";
        return false;
    }
    std::vector<DataWriteTarget> const discoveryTargets{
        {.Address = 0x1000, .Size = 4},
    };
    DataWriteTargetEvidence const discovery = EvaluateDataWriteTargetEvidence(
        0, discoveryTargets, zeroWrites, {}, {}, initial, final);
    if (discovery.Passed ||
        std::string_view(discovery.Grade) != "DISCOVERY_ONLY")
    {
        std::cerr << "data-write evidence self-test failed: discovery-only\n";
        return false;
    }
    return true;
}

bool MatchesIdentity(Module const& module, Options const& options)
{
    return (!options.ExpectedBase ||
            static_cast<uint64_t>(module.Address) == *options.ExpectedBase) &&
           module.Size == *options.ExpectedSize &&
           module.Timestamp == *options.ExpectedTimestamp &&
           module.Checksum == *options.ExpectedChecksum;
}

struct SelectedModule
{
    Module const* ModuleValue;
    ModuleInstance const* Instance;
};

SelectedModule SelectModule(IReplayEngineView const& engine, Options const& options)
{
    std::vector<Module const*> nameMatches;
    std::vector<Module const*> identityMatches;

    Module const* const modules = engine.GetModuleList();
    for (size_t index = 0; index < engine.GetModuleCount(); ++index)
    {
        Module const& module = modules[index];
        std::wstring const fullName(module.pName, module.NameLength);
        std::wstring const baseName = fs::path(fullName).filename().wstring();
        if (EqualOrdinalIgnoreCase(fullName, options.ModuleName) ||
            EqualOrdinalIgnoreCase(baseName, options.ModuleName))
        {
            nameMatches.push_back(&module);
            if (MatchesIdentity(module, options))
            {
                identityMatches.push_back(&module);
            }
        }
    }

    if (identityMatches.size() != 1)
    {
        std::cerr << "module selection expected exactly one identity match; found "
                  << identityMatches.size() << " among " << nameMatches.size()
                  << " name match(es)\n";
        for (Module const* module : nameMatches)
        {
            std::wstring const fullName(module->pName, module->NameLength);
            std::cerr << "  " << ToUtf8(fullName)
                      << " base=" << Hex(static_cast<uint64_t>(module->Address))
                      << " size=" << Hex(module->Size)
                      << " timestamp=" << Hex(module->Timestamp)
                      << " checksum=" << Hex(module->Checksum)
                      << "\n";
        }
        throw std::runtime_error("module identity selection failed");
    }

    Module const* const selected = identityMatches.front();
    std::vector<ModuleInstance const*> instances;
    ModuleInstance const* const allInstances = engine.GetModuleInstanceList();
    for (size_t index = 0; index < engine.GetModuleInstanceCount(); ++index)
    {
        if (allInstances[index].pModule == selected)
        {
            instances.push_back(&allInstances[index]);
        }
    }
    if (instances.size() != 1)
    {
        throw std::runtime_error(
            "selected module must have exactly one load instance; found " +
            std::to_string(instances.size()));
    }
    return {selected, instances.front()};
}

template <size_t Size>
std::string ByteHex(std::array<uint8_t, Size> const& bytes, size_t count)
{
    std::ostringstream output;
    output << std::hex << std::uppercase << std::setfill('0');
    for (size_t index = 0; index < std::min(count, bytes.size()); ++index)
    {
        output << std::setw(2) << static_cast<unsigned int>(bytes[index]);
    }
    return output.str();
}

bool ExpectedCountMatches(
    std::optional<uint64_t> const& expected,
    uint64_t actual) noexcept
{
    return !expected || *expected == actual;
}

void WriteOptionalCount(
    std::ostream& output,
    std::optional<uint64_t> const& value)
{
    if (value)
    {
        output << "\"" << *value << "\"";
    }
    else
    {
        output << "null";
    }
}

void WriteOptionalIndex(std::ostream& output, size_t value)
{
    if (value == kNoIndex)
    {
        output << "null";
    }
    else
    {
        output << value;
    }
}

void WriteDataWriteMemoryImage(
    std::ostream& output,
    DataWriteMemoryImage const& image)
{
    output
        << "{\"address\":\"" << Hex(image.Address) << "\""
        << ",\"valid_bytes\":" << image.Size
        << ",\"range_count\":" << image.RangeCount
        << ",\"single_range\":"
        << (image.SingleRange ? "true" : "false")
        << ",\"observation_position\":\""
        << PositionString(image.ObservationPosition) << "\""
        << ",\"observation_sequence\":\""
        << Hex(static_cast<uint64_t>(image.ObservationPosition.Sequence))
        << "\""
        << ",\"source_sequence\":\"" << Hex(image.SourceSequence) << "\""
        << ",\"source_sequence_matches_observation\":"
        << (DataWriteMemorySourceSequenceMatches(image) ? "true" : "false")
        << ",\"query_valid\":" << (image.QueryValid ? "true" : "false")
        << ",\"hex\":\"" << ByteHex(image.Bytes, image.Size) << "\"}";
}

void WriteDataWritesJsonl(
    Options const& options,
    uint64_t traceBytes,
    uint64_t targetTableBytes,
    SelectedModule const& selected,
    IReplayEngineView const& engine,
    Position const& requestedFrom,
    Position const& requestedTo,
    Position const& actualFrom,
    ReplayAccounting const& replayAccounting,
    Position const& finalPosition,
    DataWriteRecorder const& recorder,
    std::vector<DataWriteMemoryImage> const& initialImages,
    std::vector<DataWriteMemoryImage> const& finalImages,
    std::vector<DataWriteTargetEvidence> const& targetEvidence,
    GapStatistics const& gapStatistics,
    bool replayComplete,
    bool exactReplayWindow,
    bool expectationsPassed,
    bool snapshotQueriesValid,
    bool targetEvidencePassed,
    bool replayCountersSane,
    bool collectorChecksPassed)
{
    if (fs::exists(options.Output))
    {
        throw std::runtime_error(
            "output appeared during replay; refusing overwrite");
    }
    if (!options.Output.parent_path().empty())
    {
        fs::create_directories(options.Output.parent_path());
    }
    fs::path temporary = options.Output;
    temporary +=
        L".tmp-" + std::to_wstring(GetCurrentProcessId()) +
        L"-" + std::to_wstring(GetTickCount64());
    if (fs::exists(temporary))
    {
        throw std::runtime_error("temporary output path already exists");
    }
    std::ofstream output(temporary, std::ios::binary | std::ios::out);
    if (!output)
    {
        throw std::runtime_error(
            "failed to create temporary data-write JSONL");
    }

    Module const& module = *selected.ModuleValue;
    ModuleInstance const& instance = *selected.Instance;
    uint64_t const base = static_cast<uint64_t>(module.Address);
    std::wstring const moduleName(module.pName, module.NameLength);
    PositionRange const& lifetime = engine.GetLifetime();
    output
        << "{\"schema\":\"" << kDataWritesSchema
        << "\",\"kind\":\"metadata\""
        << ",\"api_package\":\"Microsoft.TimeTravelDebugging.Apis/0.9.5\""
        << ",\"trace\":\"" << JsonEscape(options.Trace.wstring()) << "\""
        << ",\"trace_bytes\":\"" << traceBytes << "\""
        << ",\"targets_tsv\":\""
        << JsonEscape(options.DataWriteTargets.wstring()) << "\""
        << ",\"targets_tsv_bytes\":\"" << targetTableBytes << "\""
        << ",\"module_requested\":\"" << JsonEscape(options.ModuleName)
        << "\""
        << ",\"module_name\":\"" << JsonEscape(moduleName) << "\""
        << ",\"module_base\":\"" << Hex(base) << "\""
        << ",\"module_size\":\"" << Hex(module.Size) << "\""
        << ",\"module_timestamp\":\"" << Hex(module.Timestamp) << "\""
        << ",\"module_checksum\":\"" << Hex(module.Checksum) << "\""
        << ",\"module_load_sequence\":\""
        << Hex(static_cast<uint64_t>(instance.LoadTime)) << "\""
        << ",\"module_unload_sequence\":\""
        << Hex(static_cast<uint64_t>(instance.UnloadTime)) << "\""
        << ",\"lifetime_min\":\"" << PositionString(lifetime.Min) << "\""
        << ",\"lifetime_max\":\"" << PositionString(lifetime.Max) << "\""
        << ",\"requested_from\":\"" << PositionString(requestedFrom) << "\""
        << ",\"requested_to\":\"" << PositionString(requestedTo) << "\""
        << ",\"actual_from\":\"" << PositionString(actualFrom) << "\""
        << ",\"processor_architecture\":\"x86\""
        << ",\"replay_mode\":\"sequential-all-segments\""
        << ",\"overwrite_phase\":\"sdk-just-before-write\""
        << ",\"write_phase\":\"sdk-as-memory-operation-observation-unclassified\""
        << ",\"callback_memory_policy\":\"thread-local-single-range-required\""
        << ",\"endpoint_memory_policy\":\"cursor-globally-conservative-single-range-required\""
        << ",\"pairing_policy\":\"exact-same-boundary-structural-candidate\""
        << ",\"raw_value_policy\":\"untyped-registers-and-bytes\""
        << ",\"promotion_policy\":\""
        << kDataWritesPromotionPolicy << "\""
        << ",\"event_limit\":\"" << options.CallContextEventLimit << "\""
        << ",\"window_semantics\":"
        << "\"state-at-from-transitions-in-open-closed-window\""
        << ",\"uint64_encoding\":\"decimal-string\""
        << "}\n";

    auto const& targets = recorder.Targets();
    auto const& counts = recorder.TargetCounts();
    auto const& pairs = recorder.Pairs();
    std::vector<uint64_t> targetPairCounts(targets.size(), 0);
    for (DataWritePair const& pair : pairs)
    {
        if (pair.ChecksPassed && pair.TargetIndex < targetPairCounts.size())
        {
            ++targetPairCounts[pair.TargetIndex];
        }
    }
    for (size_t targetIndex = 0; targetIndex < targets.size(); ++targetIndex)
    {
        DataWriteTarget const& target = targets[targetIndex];
        DataWriteTargetCounts const& observed = counts[targetIndex];
        output
            << "{\"schema\":\"" << kDataWritesSchema
            << "\",\"kind\":\"target\",\"target_index\":"
            << targetIndex
            << ",\"address\":\"" << Hex(target.Address) << "\""
            << ",\"size\":" << target.Size
            << ",\"expected_overwrite_count\":";
        WriteOptionalCount(output, target.ExpectedOverwriteCount);
        output << ",\"expected_write_count\":";
        WriteOptionalCount(output, target.ExpectedWriteCount);
        output
            << ",\"observed_overwrite_count\":\"" << observed.Overwrites
            << "\",\"observed_write_count\":\"" << observed.Writes << "\""
            << ",\"observed_pair_count\":\""
            << targetPairCounts[targetIndex] << "\""
            << ",\"initial_memory\":";
        WriteDataWriteMemoryImage(output, initialImages[targetIndex]);
        output << ",\"final_memory\":";
        WriteDataWriteMemoryImage(output, finalImages[targetIndex]);
        DataWriteTargetEvidence const& evidence = targetEvidence[targetIndex];
        output
            << ",\"evidence_grade\":\"" << evidence.Grade << "\""
            << ",\"initial_sequence_matched\":"
            << (evidence.InitialSequenceMatched ? "true" : "false")
            << ",\"final_sequence_matched\":"
            << (evidence.FinalSequenceMatched ? "true" : "false")
            << ",\"event_memory_sequence_sourced\":"
            << (evidence.EventMemorySequenceSourced ? "true" : "false")
            << ",\"transition_chain_closed\":"
            << (evidence.ChainClosed ? "true" : "false")
            << ",\"evidence_checks_passed\":"
            << (evidence.Passed ? "true" : "false")
            << ",\"expectations_passed\":"
            << (ExpectedCountMatches(
                    target.ExpectedOverwriteCount,
                    observed.Overwrites) &&
                        ExpectedCountMatches(
                            target.ExpectedWriteCount,
                            observed.Writes)
                    ? "true"
                    : "false")
            << "}\n";
    }

    auto const& events = recorder.Events();
    for (size_t eventIndex = 0; eventIndex < events.size(); ++eventIndex)
    {
        DataWriteEvent const& event = events[eventIndex];
        output
            << "{\"schema\":\"" << kDataWritesSchema
            << "\",\"kind\":\"event\",\"event_index\":" << eventIndex
            << ",\"event_type\":\""
            << JsonEscape(GetDataAccessTypeName(event.AccessType)) << "\""
            << ",\"target_index\":";
        WriteOptionalIndex(output, event.TargetIndex);
        output << ",\"pair_index\":";
        WriteOptionalIndex(output, event.PairIndex);
        output
            << ",\"intersecting_target_count\":"
            << event.IntersectingTargetCount
            << ",\"continuity_epoch\":\"" << event.ContinuityEpoch << "\""
            << ",\"position\":\"" << PositionString(event.PositionValue) << "\""
            << ",\"previous_position\":\""
            << PositionString(event.PreviousPosition) << "\""
            << ",\"unique_thread_id\":\"" << event.UniqueThreadId << "\""
            << ",\"os_thread_id\":\"" << event.ThreadId << "\""
            << ",\"pc\":\"" << Hex(event.ProgramCounter) << "\""
            << ",\"sp\":\"" << Hex(event.StackPointer) << "\""
            << ",\"fp\":\"" << Hex(event.FramePointer) << "\""
            << ",\"access_address\":\"" << Hex(event.AccessAddress) << "\""
            << ",\"access_size\":\"" << event.AccessSize << "\""
            << ",\"context_flags\":\"" << Hex(event.ContextFlags) << "\""
            << ",\"control_registers_valid\":"
            << (event.ControlRegistersValid ? "true" : "false")
            << ",\"integer_registers_valid\":"
            << (event.IntegerRegistersValid ? "true" : "false")
            << ",\"register_views_agree\":"
            << (event.RegisterViewsAgree ? "true" : "false")
            << ",\"registers\":{"
            << "\"eax\":\"" << Hex(event.Eax) << "\""
            << ",\"ebx\":\"" << Hex(event.Ebx) << "\""
            << ",\"ecx\":\"" << Hex(event.Ecx) << "\""
            << ",\"edx\":\"" << Hex(event.Edx) << "\""
            << ",\"esi\":\"" << Hex(event.Esi) << "\""
            << ",\"edi\":\"" << Hex(event.Edi) << "\""
            << ",\"ebp\":\"" << Hex(event.Ebp) << "\""
            << ",\"esp\":\"" << Hex(event.Esp) << "\""
            << ",\"eip\":\"" << Hex(event.Eip) << "\""
            << ",\"eflags\":\"" << Hex(event.EFlags) << "\"}"
            << ",\"observed_memory\":";
        WriteDataWriteMemoryImage(output, event.ObservedMemory);
        output << "}\n";
    }

    for (size_t pairIndex = 0; pairIndex < pairs.size(); ++pairIndex)
    {
        DataWritePair const& pair = pairs[pairIndex];
        output
            << "{\"schema\":\"" << kDataWritesSchema
            << "\",\"kind\":\"pair\",\"pair_index\":" << pairIndex
            << ",\"target_index\":" << pair.TargetIndex
            << ",\"overwrite_event_index\":" << pair.OverwriteEventIndex
            << ",\"write_event_index\":" << pair.WriteEventIndex
            << ",\"continuity_epoch\":\"" << pair.ContinuityEpoch << "\""
            << ",\"grade\":\"STRUCTURAL_WRITE_PAIR\""
            << ",\"checks_passed\":"
            << (pair.ChecksPassed ? "true" : "false")
            << ",\"changed\":" << (pair.Changed ? "true" : "false")
            << "}\n";
    }

    for (uint64_t ordinal = 0;
         ordinal < recorder.ContinuityBreakCount();
         ++ordinal)
    {
        output
            << "{\"schema\":\"" << kDataWritesSchema
            << "\",\"kind\":\"continuity-break\""
            << ",\"ordinal\":\"" << ordinal << "\"}\n";
    }

    output
        << "{\"schema\":\"" << kDataWritesSchema
        << "\",\"kind\":\"gap-summary\",\"total\":\""
        << gapStatistics.Total() << "\""
        << ",\"kind_no_gap\":\"" << gapStatistics.KindCount(0) << "\""
        << ",\"kind_context_switch\":\"" << gapStatistics.KindCount(1)
        << "\""
        << ",\"kind_unrecorded\":\"" << gapStatistics.KindCount(2) << "\""
        << ",\"kind_large\":\"" << gapStatistics.KindCount(3) << "\"";
    for (size_t index = 0; index < 17; ++index)
    {
        output
            << ",\"event_"
            << JsonEscape(GetGapEventTypeName(static_cast<GapEventType>(index)))
            << "\":\"" << gapStatistics.EventCount(index) << "\"";
    }
    output << "}\n";

    char const* const stopReason =
        GetEventTypeName(replayAccounting.StopReason);
    output
        << "{\"schema\":\"" << kDataWritesSchema
        << "\",\"kind\":\"summary\""
        << ",\"target_count\":" << targets.size()
        << ",\"event_count\":" << events.size()
        << ",\"pair_count\":\"" << pairs.size() << "\""
        << ",\"orphan_event_count\":\""
        << (events.size() - pairs.size() * 2) << "\""
        << ",\"callback_hits\":\"" << recorder.CallbackHits() << "\""
        << ",\"ambiguous_callbacks\":\""
        << recorder.AmbiguousCallbacks() << "\""
        << ",\"nontrivial_gap_count\":\""
        << recorder.NontrivialGapCount() << "\""
        << ",\"continuity_break_count\":\""
        << recorder.ContinuityBreakCount() << "\""
        << ",\"instructions_executed\":\""
        << replayAccounting.InstructionsExecuted << "\""
        << ",\"steps_executed\":\"" << replayAccounting.StepsExecuted << "\""
        << ",\"replay_counters_sane\":"
        << (replayCountersSane ? "true" : "false")
        << ",\"truncated\":" << (recorder.Truncated() ? "true" : "false")
        << ",\"callback_failed\":"
        << (recorder.CallbackFailed() ? "true" : "false")
        << ",\"ordering_valid\":"
        << (recorder.OrderingValid() ? "true" : "false")
        << ",\"contexts_valid\":"
        << (recorder.ContextsValid() ? "true" : "false")
        << ",\"pairing_valid\":"
        << (recorder.PairingValid() ? "true" : "false")
        << ",\"pairing_complete\":"
        << (recorder.PairingComplete() ? "true" : "false")
        << ",\"snapshot_queries_valid\":"
        << (snapshotQueriesValid ? "true" : "false")
        << ",\"target_evidence_passed\":"
        << (targetEvidencePassed ? "true" : "false")
        << ",\"exact_replay_window\":"
        << (exactReplayWindow ? "true" : "false")
        << ",\"expectations_passed\":"
        << (expectationsPassed ? "true" : "false")
        << ",\"stop_reason\":\""
        << JsonEscape(stopReason == nullptr ? "" : stopReason) << "\""
        << ",\"replay_chunks\":\"" << replayAccounting.ChunkCount << "\""
        << ",\"replay_chunk_steps\":\"" << kReplayChunkSteps << "\""
        << ",\"final_position\":\"" << PositionString(finalPosition) << "\""
        << ",\"replay_complete\":" << (replayComplete ? "true" : "false")
        << ",\"collector_checks_passed\":"
        << (collectorChecksPassed ? "true" : "false")
        << "}\n";
    output.flush();
    if (!output)
    {
        throw std::runtime_error(
            "failed while writing data-write output JSONL");
    }
    output.close();
    if (output.fail())
    {
        throw std::runtime_error(
            "failed while closing data-write output JSONL");
    }
    if (!MoveFileExW(
            temporary.c_str(),
            options.Output.c_str(),
            MOVEFILE_WRITE_THROUGH))
    {
        throw std::runtime_error(
            "failed to atomically publish data-write JSONL; Win32 error " +
            std::to_string(GetLastError()));
    }
}

void WriteCallContextJsonl(
    Options const& options,
    uint64_t traceBytes,
    uint64_t targetTableBytes,
    SelectedModule const& selected,
    IReplayEngineView const& engine,
    Position const& requestedFrom,
    Position const& requestedTo,
    ReplayAccounting const& replayAccounting,
    Position const& finalPosition,
    CallContextRecorder const& recorder,
    GapStatistics const& gapStatistics,
    bool replayComplete,
    bool expectationsPassed,
    bool pairingExpectationsPassed,
    bool replayCountersSane,
    bool collectorChecksPassed)
{
    if (fs::exists(options.Output))
    {
        throw std::runtime_error(
            "output appeared during replay; refusing overwrite");
    }
    if (!options.Output.parent_path().empty())
    {
        fs::create_directories(options.Output.parent_path());
    }
    fs::path temporary = options.Output;
    temporary +=
        L".tmp-" + std::to_wstring(GetCurrentProcessId()) +
        L"-" + std::to_wstring(GetTickCount64());
    if (fs::exists(temporary))
    {
        throw std::runtime_error("temporary output path already exists");
    }
    std::ofstream output(temporary, std::ios::binary | std::ios::out);
    if (!output)
    {
        throw std::runtime_error(
            "failed to create temporary call-context JSONL");
    }

    Module const& module = *selected.ModuleValue;
    ModuleInstance const& instance = *selected.Instance;
    uint64_t const base = static_cast<uint64_t>(module.Address);
    std::wstring const moduleName(module.pName, module.NameLength);
    PositionRange const& lifetime = engine.GetLifetime();
    output
        << "{\"schema\":\"" << kCallContextSchema
        << "\",\"kind\":\"metadata\""
        << ",\"api_package\":\"Microsoft.TimeTravelDebugging.Apis/0.9.5\""
        << ",\"trace\":\"" << JsonEscape(options.Trace.wstring()) << "\""
        << ",\"trace_bytes\":\"" << traceBytes << "\""
        << ",\"targets_tsv\":\""
        << JsonEscape(options.CallContextTargets.wstring()) << "\""
        << ",\"targets_tsv_bytes\":\"" << targetTableBytes << "\""
        << ",\"module_requested\":\"" << JsonEscape(options.ModuleName)
        << "\""
        << ",\"module_name\":\"" << JsonEscape(moduleName) << "\""
        << ",\"module_base\":\"" << Hex(base) << "\""
        << ",\"module_size\":\"" << Hex(module.Size) << "\""
        << ",\"module_timestamp\":\"" << Hex(module.Timestamp) << "\""
        << ",\"module_checksum\":\"" << Hex(module.Checksum) << "\""
        << ",\"module_load_sequence\":\""
        << Hex(static_cast<uint64_t>(instance.LoadTime)) << "\""
        << ",\"module_unload_sequence\":\""
        << Hex(static_cast<uint64_t>(instance.UnloadTime)) << "\""
        << ",\"lifetime_min\":\"" << PositionString(lifetime.Min) << "\""
        << ",\"lifetime_max\":\"" << PositionString(lifetime.Max) << "\""
        << ",\"requested_from\":\"" << PositionString(requestedFrom) << "\""
        << ",\"requested_to\":\"" << PositionString(requestedTo) << "\""
        << ",\"processor_architecture\":\"x86\""
        << ",\"replay_mode\":\"sequential-all-segments\""
        << ",\"entry_phase\":\"execute-watchpoint-before-entry-instruction\""
        << ",\"call_phase\":\"callback-position-at-call-instruction\""
        << ",\"return_phase\":\"callback-position-at-ret-instruction\""
        << ",\"association_policy\":"
        << "\"global-epoch-breaks-on-every-non-no-gap-and-continuity-callback\""
        << ",\"raw_value_policy\":\"untyped-registers-and-bytes\""
        << ",\"stack_bytes_requested\":"
        << options.CallContextStackBytes
        << ",\"event_limit\":\"" << options.CallContextEventLimit << "\""
        << ",\"window_semantics\":\"inclusive-position-bounds\""
        << ",\"uint64_encoding\":\"decimal-string\""
        << "}\n";

    auto const& targets = recorder.Targets();
    auto const& counts = recorder.TargetCounts();
    auto const& invocations = recorder.Invocations();
    auto const& events = recorder.Events();
    std::vector<uint64_t> callEntryPairs(targets.size(), 0);
    std::vector<uint64_t> validatedReturns(targets.size(), 0);
    std::vector<uint64_t> orphanReturns(targets.size(), 0);
    std::vector<uint64_t> gapFreeEnvelopes(targets.size(), 0);
    for (CallContextInvocation const& invocation : invocations)
    {
        if (invocation.CallEntryChecksPassed)
        {
            ++callEntryPairs[invocation.TargetIndex];
        }
        if (invocation.Grade == CallContextInvocationGrade::CallEntryReturn)
        {
            ++validatedReturns[invocation.TargetIndex];
        }
        if (invocation.Grade == CallContextInvocationGrade::CallEntryReturn)
        {
            ++gapFreeEnvelopes[invocation.TargetIndex];
        }
    }
    for (CallContextEvent const& event : events)
    {
        if (event.Kind == CallContextEventKind::Return &&
            event.InvocationIndex == kNoIndex)
        {
            ++orphanReturns[event.TargetIndex];
        }
    }
    uint64_t const rawReturnCount = std::accumulate(
        counts.begin(),
        counts.end(),
        uint64_t{0},
        [](uint64_t total, CallContextTargetCounts const& value)
        {
            return total + value.Returns;
        });
    uint64_t const validatedReturnCount = std::accumulate(
        validatedReturns.begin(), validatedReturns.end(), uint64_t{0});
    uint64_t const orphanReturnCount = std::accumulate(
        orphanReturns.begin(), orphanReturns.end(), uint64_t{0});
    if (!CallContextReturnAccountingCloses(
            rawReturnCount, validatedReturnCount, orphanReturnCount))
    {
        throw std::runtime_error(
            "call-context aggregate return/orphan accounting does not close");
    }
    uint64_t const expectedAssociationBarriers =
        gapStatistics.KindCount(1) +
        gapStatistics.KindCount(2) +
        gapStatistics.KindCount(3) +
        recorder.ContinuityBreakCallbacks();
    if (recorder.AssociationBarrierCount() != expectedAssociationBarriers)
    {
        throw std::runtime_error(
            "call-context association-barrier accounting does not close");
    }
    for (size_t targetIndex = 0; targetIndex < targets.size(); ++targetIndex)
    {
        CallContextTarget const& target = targets[targetIndex];
        CallContextTargetCounts const& observed = counts[targetIndex];
        if (!CallContextReturnAccountingCloses(
                observed.Returns,
                validatedReturns[targetIndex],
                orphanReturns[targetIndex]))
        {
            throw std::runtime_error(
                "call-context target return/orphan accounting does not close");
        }
        output
            << "{\"schema\":\"" << kCallContextSchema
            << "\",\"kind\":\"target\",\"target_index\":"
            << targetIndex
            << ",\"entry_rva\":\"" << Hex(target.EntryRva) << "\""
            << ",\"entry_va\":\"" << Hex(base + target.EntryRva) << "\""
            << ",\"ranges\":[";
        for (size_t rangeIndex = 0;
             rangeIndex < target.Ranges.size();
             ++rangeIndex)
        {
            if (rangeIndex != 0)
            {
                output << ',';
            }
            Range const& range = target.Ranges[rangeIndex];
            output
                << "{\"rva_start\":\"" << Hex(range.Min)
                << "\",\"rva_end_exclusive\":\"" << Hex(range.Max)
                << "\"}";
        }
        output << "]"
               << ",\"expected_entry_count\":";
        WriteOptionalCount(output, target.ExpectedEntryCount);
        output << ",\"expected_call_count\":";
        WriteOptionalCount(output, target.ExpectedCallCount);
        output << ",\"expected_return_count\":";
        WriteOptionalCount(output, target.ExpectedReturnCount);
        output
            << ",\"observed_entry_count\":\"" << observed.Entries << "\""
             << ",\"observed_call_count\":\"" << observed.Calls << "\""
             << ",\"observed_return_count\":\"" << observed.Returns << "\""
             << ",\"observed_call_entry_pair_count\":\""
             << callEntryPairs[targetIndex] << "\""
             << ",\"observed_validated_return_count\":\""
             << validatedReturns[targetIndex] << "\""
             << ",\"observed_orphan_return_count\":\""
             << orphanReturns[targetIndex] << "\""
             << ",\"observed_gap_free_envelope_count\":\""
             << gapFreeEnvelopes[targetIndex] << "\""
            << ",\"expectations_passed\":"
            << (ExpectedCountMatches(target.ExpectedEntryCount, observed.Entries) &&
                        ExpectedCountMatches(target.ExpectedCallCount, observed.Calls) &&
                        ExpectedCountMatches(target.ExpectedReturnCount, observed.Returns)
                    ? "true"
                    : "false")
            << "}\n";
    }

    for (size_t eventIndex = 0; eventIndex < events.size(); ++eventIndex)
    {
        CallContextEvent const& event = events[eventIndex];
        uint64_t const edxEax =
            (static_cast<uint64_t>(event.Edx) << 32) | event.Eax;
        output
            << "{\"schema\":\"" << kCallContextSchema
            << "\",\"kind\":\"event\",\"event_index\":" << eventIndex
            << ",\"event_type\":\""
            << GetCallContextEventKindName(event.Kind) << "\""
            << ",\"target_index\":" << event.TargetIndex
            << ",\"invocation_index\":";
        WriteOptionalIndex(output, event.InvocationIndex);
        output
            << ",\"association_epoch\":\"" << event.AssociationEpoch << "\""
            << ",\"position\":\"" << PositionString(event.PositionValue) << "\""
            << ",\"previous_position\":\""
            << PositionString(event.PreviousPosition) << "\""
            << ",\"unique_thread_id\":\"" << event.UniqueThreadId << "\""
            << ",\"os_thread_id\":\"" << event.ThreadId << "\""
            << ",\"pc\":\"" << Hex(event.ProgramCounter) << "\""
            << ",\"sp\":\"" << Hex(event.StackPointer) << "\""
            << ",\"fp\":\"" << Hex(event.FramePointer) << "\""
            << ",\"instruction_target\":\""
            << Hex(event.InstructionTarget) << "\""
            << ",\"fallthrough\":\"" << Hex(event.FallThrough) << "\""
            << ",\"context_flags\":\"" << Hex(event.ContextFlags) << "\""
            << ",\"control_registers_valid\":"
            << (event.ControlRegistersValid ? "true" : "false")
            << ",\"integer_registers_valid\":"
            << (event.IntegerRegistersValid ? "true" : "false")
            << ",\"register_views_agree\":"
            << (event.RegisterViewsAgree ? "true" : "false")
            << ",\"registers\":{"
            << "\"eax\":\"" << Hex(event.Eax) << "\""
            << ",\"ebx\":\"" << Hex(event.Ebx) << "\""
            << ",\"ecx\":\"" << Hex(event.Ecx) << "\""
            << ",\"edx\":\"" << Hex(event.Edx) << "\""
            << ",\"esi\":\"" << Hex(event.Esi) << "\""
            << ",\"edi\":\"" << Hex(event.Edi) << "\""
            << ",\"ebp\":\"" << Hex(event.Ebp) << "\""
            << ",\"esp\":\"" << Hex(event.Esp) << "\""
            << ",\"eip\":\"" << Hex(event.Eip) << "\""
            << ",\"eflags\":\"" << Hex(event.EFlags) << "\"}"
            << ",\"raw_edx_eax\":\"" << Hex(edxEax) << "\""
            << ",\"basic_return_value_untyped\":\""
            << Hex(event.BasicReturnValue) << "\""
            << ",\"stack\":{\"address\":\""
            << Hex(event.StackMemoryAddress) << "\""
            << ",\"requested_bytes\":" << options.CallContextStackBytes
            << ",\"valid_bytes\":" << event.StackMemorySize
            << ",\"query_valid\":"
            << (event.StackMemoryQueryValid ? "true" : "false")
            << ",\"hex\":\""
            << ByteHex(event.StackMemory, event.StackMemorySize) << "\"}"
            << ",\"instruction_bytes\":{\"address\":\""
            << Hex(event.InstructionMemoryAddress) << "\""
            << ",\"valid_bytes\":" << event.InstructionMemorySize
            << ",\"query_valid\":"
            << (event.InstructionMemoryQueryValid ? "true" : "false")
            << ",\"hex\":\""
            << ByteHex(event.InstructionMemory, event.InstructionMemorySize)
            << "\"}"
            << ",\"decoded_near_return\":"
            << (event.DecodedNearReturn ? "true" : "false")
            << "}\n";
    }

    for (size_t invocationIndex = 0;
         invocationIndex < invocations.size();
         ++invocationIndex)
    {
        CallContextInvocation const& invocation = invocations[invocationIndex];
        output
            << "{\"schema\":\"" << kCallContextSchema
            << "\",\"kind\":\"invocation\",\"invocation_index\":"
            << invocationIndex
            << ",\"target_index\":" << invocation.TargetIndex
            << ",\"unique_thread_id\":\"" << invocation.UniqueThreadId << "\""
            << ",\"association_epoch\":\""
            << invocation.AssociationEpoch << "\""
            << ",\"call_event_index\":";
        WriteOptionalIndex(output, invocation.CallEventIndex);
        output << ",\"entry_event_index\":";
        WriteOptionalIndex(output, invocation.EntryEventIndex);
        output << ",\"return_event_index\":";
        WriteOptionalIndex(output, invocation.ReturnEventIndex);
        output
            << ",\"grade\":\""
            << GetCallContextInvocationGradeName(invocation.Grade) << "\""
            << ",\"call_entry_checks_passed\":"
            << (invocation.CallEntryChecksPassed ? "true" : "false")
            << ",\"return_checks_passed\":"
            << (invocation.ReturnChecksPassed ? "true" : "false")
            << ",\"gap_crossed\":"
            << (invocation.GapCrossed ? "true" : "false")
            << ",\"continuity_break_crossed\":"
            << (invocation.ContinuityBreakCrossed ? "true" : "false")
            << "}\n";
    }

    output
        << "{\"schema\":\"" << kCallContextSchema
        << "\",\"kind\":\"gap-summary\",\"total\":\""
        << gapStatistics.Total() << "\""
        << ",\"kind_no_gap\":\"" << gapStatistics.KindCount(0) << "\""
        << ",\"kind_context_switch\":\"" << gapStatistics.KindCount(1)
        << "\""
        << ",\"kind_unrecorded\":\"" << gapStatistics.KindCount(2) << "\""
        << ",\"kind_large\":\"" << gapStatistics.KindCount(3) << "\"";
    for (size_t index = 0; index < 17; ++index)
    {
        output
            << ",\"event_"
            << JsonEscape(GetGapEventTypeName(static_cast<GapEventType>(index)))
            << "\":\"" << gapStatistics.EventCount(index) << "\"";
    }
    output << "}\n";

    char const* const stopReason =
        GetEventTypeName(replayAccounting.StopReason);
    output
        << "{\"schema\":\"" << kCallContextSchema
        << "\",\"kind\":\"summary\""
        << ",\"target_count\":" << targets.size()
        << ",\"event_count\":" << events.size()
         << ",\"invocation_count\":" << invocations.size()
         << ",\"call_entry_pair_count\":\""
         << std::accumulate(callEntryPairs.begin(), callEntryPairs.end(), uint64_t{0})
         << "\""
         << ",\"validated_return_count\":\""
         << validatedReturnCount
         << "\""
         << ",\"raw_return_count\":\"" << rawReturnCount << "\""
         << ",\"orphan_return_count\":\""
         << orphanReturnCount
         << "\""
         << ",\"gap_free_envelope_count\":\""
         << std::accumulate(gapFreeEnvelopes.begin(), gapFreeEnvelopes.end(), uint64_t{0})
         << "\""
        << ",\"call_return_callbacks\":\""
        << recorder.CallReturnCallbacks() << "\""
        << ",\"entry_callbacks\":\"" << recorder.EntryCallbacks() << "\""
        << ",\"continuity_break_callbacks\":\""
        << recorder.ContinuityBreakCallbacks() << "\""
        << ",\"association_barrier_count\":\""
        << recorder.AssociationBarrierCount() << "\""
        << ",\"final_association_epoch\":\""
        << recorder.AssociationBarrierCount() << "\""
        << ",\"instructions_executed\":\""
        << replayAccounting.InstructionsExecuted << "\""
        << ",\"steps_executed\":\"" << replayAccounting.StepsExecuted << "\""
        << ",\"replay_counters_sane\":"
        << (replayCountersSane ? "true" : "false")
        << ",\"truncated\":" << (recorder.Truncated() ? "true" : "false")
        << ",\"callback_failed\":"
        << (recorder.CallbackFailed() ? "true" : "false")
        << ",\"ordering_valid\":"
        << (recorder.OrderingValid() ? "true" : "false")
        << ",\"contexts_valid\":"
        << (recorder.ContextsValid() ? "true" : "false")
        << ",\"expectations_passed\":"
        << (expectationsPassed ? "true" : "false")
        << ",\"pairing_expectations_passed\":"
        << (pairingExpectationsPassed ? "true" : "false")
        << ",\"stop_reason\":\""
        << JsonEscape(stopReason == nullptr ? "" : stopReason) << "\""
        << ",\"replay_chunks\":\"" << replayAccounting.ChunkCount << "\""
        << ",\"replay_chunk_steps\":\"" << kReplayChunkSteps << "\""
        << ",\"final_position\":\"" << PositionString(finalPosition) << "\""
        << ",\"replay_complete\":" << (replayComplete ? "true" : "false")
        << ",\"collector_checks_passed\":"
        << (collectorChecksPassed ? "true" : "false")
        << "}\n";
    output.flush();
    if (!output)
    {
        throw std::runtime_error(
            "failed while writing call-context output JSONL");
    }
    output.close();
    if (output.fail())
    {
        throw std::runtime_error(
            "failed while closing call-context output JSONL");
    }
    if (!MoveFileExW(
            temporary.c_str(),
            options.Output.c_str(),
            MOVEFILE_WRITE_THROUGH))
    {
        throw std::runtime_error(
            "failed to atomically publish call-context JSONL; Win32 error " +
            std::to_string(GetLastError()));
    }
}

void WriteJsonl(
    Options const& options,
    uint64_t traceBytes,
    SelectedModule const& selected,
    IReplayEngineView const& engine,
    Position const& requestedFrom,
    Position const& requestedTo,
    ReplayAccounting const& replayAccounting,
    Position const& finalPosition,
    AtomicCoverage const& coverage,
    GapStatistics const& gapStatistics,
    std::vector<Range> const& ranges,
    bool replayComplete,
    bool markerAssertionsPassed,
    bool collectorChecksPassed,
    bool countersQuarantined)
{
    if (fs::exists(options.Output))
    {
        throw std::runtime_error("output appeared during replay; refusing overwrite");
    }
    if (!options.Output.parent_path().empty())
    {
        fs::create_directories(options.Output.parent_path());
    }
    fs::path temporary = options.Output;
    temporary +=
        L".tmp-" + std::to_wstring(GetCurrentProcessId()) +
        L"-" + std::to_wstring(GetTickCount64());
    if (fs::exists(temporary))
    {
        throw std::runtime_error("temporary output path already exists");
    }
    std::ofstream output(temporary, std::ios::binary | std::ios::out);
    if (!output)
    {
        throw std::runtime_error("failed to create temporary output JSONL");
    }

    Module const& module = *selected.ModuleValue;
    ModuleInstance const& instance = *selected.Instance;
    uint64_t const base = static_cast<uint64_t>(module.Address);
    std::wstring const moduleName(module.pName, module.NameLength);
    PositionRange const& lifetime = engine.GetLifetime();

    output
        << "{\"schema\":\"" << kSchema << "\",\"kind\":\"metadata\""
        << ",\"upstream_commit\":\"1b0b2f336f959c1caadcd51bb2c82149a9bce2d5\""
        << ",\"api_package\":\"Microsoft.TimeTravelDebugging.Apis/0.9.5\""
        << ",\"trace\":\"" << JsonEscape(options.Trace.wstring()) << "\""
        << ",\"trace_bytes\":\"" << traceBytes << "\""
        << ",\"module_requested\":\"" << JsonEscape(options.ModuleName) << "\""
        << ",\"module_name\":\"" << JsonEscape(moduleName) << "\""
        << ",\"module_base\":\"" << Hex(base) << "\""
        << ",\"module_size\":\"" << Hex(module.Size) << "\""
        << ",\"module_timestamp\":\"" << Hex(module.Timestamp) << "\""
        << ",\"module_checksum\":\"" << Hex(module.Checksum) << "\""
        << ",\"module_load_sequence\":\""
        << Hex(static_cast<uint64_t>(instance.LoadTime)) << "\""
        << ",\"module_unload_sequence\":\""
        << Hex(static_cast<uint64_t>(instance.UnloadTime)) << "\""
        << ",\"lifetime_min\":\"" << PositionString(lifetime.Min) << "\""
        << ",\"lifetime_max\":\"" << PositionString(lifetime.Max) << "\""
        << ",\"requested_from\":\"" << PositionString(requestedFrom) << "\""
        << ",\"requested_to\":\"" << PositionString(requestedTo) << "\""
        << ",\"watchpoint_access\":\"execute\""
        << ",\"range_semantics\":\"half-open-byte-ranges\""
        << ",\"window_semantics\":\"inclusive-position-bounds\""
        << ",\"collector\":\"parallel-safe-atomic-byte-bitmap\""
        << ",\"replay_mode\":\""
        << (options.Sequential ? "sequential" : "parallel") << "\""
        << ",\"step_accounting\":\"chunked-64-bit-accumulation\""
        << ",\"uint64_encoding\":\"decimal-string\""
        << "}\n";

    uint64_t coveredBytes = 0;
    for (size_t index = 0; index < ranges.size(); ++index)
    {
        Range const& range = ranges[index];
        uint64_t const byteCount = range.Max - range.Min;
        coveredBytes += byteCount;
        output
            << "{\"schema\":\"" << kSchema << "\",\"kind\":\"range\""
            << ",\"index\":" << index
            << ",\"rva_start\":\"" << Hex(range.Min) << "\""
            << ",\"rva_end_exclusive\":\"" << Hex(range.Max) << "\""
            << ",\"va_start\":\"" << Hex(base + range.Min) << "\""
            << ",\"va_end_exclusive\":\"" << Hex(base + range.Max) << "\""
            << ",\"byte_count\":" << byteCount
            << "}\n";
    }

    auto writeAssertion =
        [&](char const* expectation, uint64_t rva, bool observed, bool pass)
        {
            output
                << "{\"schema\":\"" << kSchema << "\",\"kind\":\"assertion\""
                << ",\"expectation\":\"" << expectation << "\""
                << ",\"rva\":\"" << Hex(rva) << "\""
                << ",\"va\":\"" << Hex(base + rva) << "\""
                << ",\"observed\":" << (observed ? "true" : "false")
                << ",\"pass\":" << (pass ? "true" : "false")
                << "}\n";
        };

    for (uint64_t const rva : options.MustHitRvas)
    {
        bool const observed = coverage.IsCovered(rva);
        writeAssertion("hit", rva, observed, observed);
    }
    for (uint64_t const rva : options.MustMissRvas)
    {
        bool const observed = coverage.IsCovered(rva);
        writeAssertion("miss", rva, observed, !observed);
    }

    output
        << "{\"schema\":\"" << kSchema << "\",\"kind\":\"gap-summary\""
        << ",\"total\":\"" << gapStatistics.Total() << "\""
        << ",\"kind_no_gap\":\"" << gapStatistics.KindCount(0) << "\""
        << ",\"kind_context_switch\":\"" << gapStatistics.KindCount(1) << "\""
        << ",\"kind_unrecorded\":\"" << gapStatistics.KindCount(2) << "\""
        << ",\"kind_large\":\"" << gapStatistics.KindCount(3) << "\"";
    for (size_t index = 0; index < 17; ++index)
    {
        output
            << ",\"event_" << JsonEscape(
                GetGapEventTypeName(static_cast<GapEventType>(index)))
            << "\":\"" << gapStatistics.EventCount(index) << "\"";
    }
    output << "}\n";

    char const* const stopReason =
        GetEventTypeName(replayAccounting.StopReason);
    output
        << "{\"schema\":\"" << kSchema << "\",\"kind\":\"summary\""
        << ",\"range_count\":" << ranges.size()
        << ",\"covered_bytes\":\"" << coveredBytes << "\"";

    // A quarantined summary withholds every counter the engine mis-reported.
    // Absent, not zero and not the broken value: a reader that wants a step
    // count must fail to find one rather than silently read a wrong number.
    // The raw values survive under quarantined_counters as evidence.
    if (countersQuarantined)
    {
        output
            << ",\"counters_quarantined\":true"
            << ",\"quarantined_counters\":{"
            << "\"callback_hits\":\"" << coverage.CallbackHits() << "\""
            << ",\"instructions_executed\":\""
            << replayAccounting.InstructionsExecuted << "\""
            << ",\"steps_executed\":\"" << replayAccounting.StepsExecuted << "\""
            << ",\"gap_events\":\"" << gapStatistics.Total() << "\""
            << ",\"reason\":\"" << JsonEscape(kQuarantineReason) << "\""
            << "}";
    }
    else
    {
        output
            << ",\"counters_quarantined\":false"
            << ",\"callback_hits\":\"" << coverage.CallbackHits() << "\""
            << ",\"instructions_executed\":\""
            << replayAccounting.InstructionsExecuted << "\""
            << ",\"steps_executed\":\"" << replayAccounting.StepsExecuted
            << "\"";
    }

    output
        << ",\"stop_reason\":\""
        << JsonEscape(stopReason == nullptr ? "" : stopReason) << "\""
        << ",\"replay_chunks\":\"" << replayAccounting.ChunkCount << "\""
        << ",\"replay_chunk_steps\":\"" << kReplayChunkSteps << "\""
        << ",\"final_position\":\"" << PositionString(finalPosition) << "\""
        << ",\"replay_complete\":" << (replayComplete ? "true" : "false")
        << ",\"marker_assertions_passed\":"
        << (markerAssertionsPassed ? "true" : "false")
        << ",\"collector_checks_passed\":"
        << (collectorChecksPassed ? "true" : "false")
        << "}\n";
    output.flush();
    if (!output)
    {
        throw std::runtime_error("failed while writing output JSONL");
    }
    output.close();
    if (output.fail())
    {
        throw std::runtime_error("failed while closing output JSONL");
    }
    if (!MoveFileExW(
            temporary.c_str(),
            options.Output.c_str(),
            MOVEFILE_WRITE_THROUGH))
    {
        throw std::runtime_error(
            "failed to atomically publish output JSONL; Win32 error " +
            std::to_string(GetLastError()));
    }
}

int AnalyzeDataWrites(Options const& options)
{
    uint64_t const traceBytesBefore = fs::file_size(options.Trace);
    fs::file_time_type const traceWriteBefore = fs::last_write_time(options.Trace);
    uint64_t const targetTableBytesBefore =
        fs::file_size(options.DataWriteTargets);
    fs::file_time_type const targetTableWriteBefore =
        fs::last_write_time(options.DataWriteTargets);

    auto [ownedEngine, createResult] = MakeReplayEngine();
    if (createResult != 0 || !ownedEngine)
    {
        std::cerr << "CreateReplayEngine failed: " << createResult << "\n";
        return 3;
    }
    if (!ownedEngine->Initialize(options.Trace.c_str()))
    {
        std::cerr << "IReplayEngine::Initialize failed\n";
        return 3;
    }

    SelectedModule const selected = SelectModule(*ownedEngine, options);
    Module const& module = *selected.ModuleValue;
    ModuleInstance const& instance = *selected.Instance;
    uint64_t const base = static_cast<uint64_t>(module.Address);
    if (module.Size == 0 ||
        module.Size > options.MaxModuleBytes ||
        module.Size > std::numeric_limits<uint64_t>::max() - base ||
        base > std::numeric_limits<uint32_t>::max() ||
        base + module.Size > uint64_t{1} + std::numeric_limits<uint32_t>::max())
    {
        throw std::runtime_error(
            "selected module is not a bounded 32-bit data-write identity");
    }
    if (ownedEngine->GetSystemInfo().System.ProcessorArchitecture !=
        PROCESSOR_ARCHITECTURE_INTEL)
    {
        throw std::runtime_error("data-writes mode requires an x86 trace");
    }

    PositionRange const& lifetime = ownedEngine->GetLifetime();
    Position const requestedFrom = *options.From;
    Position const requestedTo = *options.To;
    Position const replayLimit = requestedTo;
    if (requestedFrom < lifetime.Min ||
        requestedFrom > lifetime.Max ||
        requestedTo < lifetime.Min ||
        requestedTo > lifetime.Max ||
        requestedFrom >= requestedTo)
    {
        throw std::runtime_error(
            "requested replay window lies outside trace lifetime");
    }
    if (requestedFrom.Sequence < instance.LoadTime ||
        (instance.UnloadTime != TTD::SequenceId::Max &&
         requestedTo.Sequence >= instance.UnloadTime))
    {
        throw std::runtime_error(
            "selected module is not active for the complete requested window");
    }

    std::vector<DataWriteTarget> targets =
        ReadDataWriteTargets(options.DataWriteTargets);
    GapStatistics gapStatistics;
    DataWriteRecorder recorder(
        std::move(targets),
        options.CallContextEventLimit,
        gapStatistics);
    UniqueCursor cursor{ownedEngine->NewCursor()};
    if (!cursor)
    {
        throw std::runtime_error("IReplayEngine::NewCursor failed");
    }
    cursor->SetReplayFlags(
        ReplayFlags::ReplayAllSegmentsWithoutFiltering |
        ReplayFlags::ReplaySegmentsSequentially);
    cursor->SetDefaultMemoryPolicy(QueryMemoryPolicy::GloballyConservative);
    for (DataWriteTarget const& target : recorder.Targets())
    {
        bool const added = cursor->AddMemoryWatchpoint(
            MemoryWatchpointData
            {
                .Address = static_cast<TTD::GuestAddress>(target.Address),
                .Size = target.Size,
                .AccessMask = DataAccessMask::Write | DataAccessMask::Overwrite,
            });
        if (!added)
        {
            throw std::runtime_error(
                "AddMemoryWatchpoint failed for data-write target " +
                Hex(target.Address));
        }
    }
    cursor->SetMemoryWatchpointCallback(
        DataWriteMemoryCallback,
        reinterpret_cast<uintptr_t>(&recorder));
    cursor->SetThreadContinuityBreakCallback(
        DataWriteContinuityBreakCallback,
        reinterpret_cast<uintptr_t>(&recorder));
    cursor->SetGapKindMask(GapKindMask::All);
    cursor->SetGapEventMask(GapEventMask::All);
    cursor->SetGapEventCallback(
        DataWriteGapCallback,
        reinterpret_cast<uintptr_t>(&recorder));
    cursor->SetEventMask(EventMask::MemoryWatchpoint | EventMask::Gap);
    cursor->SetPosition(requestedFrom);
    Position const actualFrom = cursor->GetPosition();

    std::vector<DataWriteMemoryImage> initialImages;
    initialImages.reserve(recorder.Targets().size());
    for (DataWriteTarget const& target : recorder.Targets())
    {
        initialImages.push_back(QueryExactDataWriteMemory(*cursor, target));
    }

    std::cerr
        << "replaying data-write trace; module="
        << ToUtf8(std::wstring(module.pName, module.NameLength))
        << " base=" << Hex(base)
        << " size=" << Hex(module.Size)
        << " targets=" << recorder.Targets().size()
        << " from=" << PositionString(requestedFrom)
        << " to=" << PositionString(requestedTo)
        << " mode=sequential raw-phase-calibration\n";
    ReplayAccounting const replayAccounting = AccumulateReplayChunks(
        [&cursor, &replayLimit]()
        {
            return cursor->ReplayForward(
                replayLimit,
                static_cast<StepCount>(kReplayChunkSteps));
        });
    Position const finalPosition = cursor->GetPosition();

    std::vector<DataWriteMemoryImage> finalImages;
    finalImages.reserve(recorder.Targets().size());
    for (DataWriteTarget const& target : recorder.Targets())
    {
        finalImages.push_back(QueryExactDataWriteMemory(*cursor, target));
    }

    uint64_t const traceBytesAfter = fs::file_size(options.Trace);
    fs::file_time_type const traceWriteAfter = fs::last_write_time(options.Trace);
    if (traceBytesAfter != traceBytesBefore || traceWriteAfter != traceWriteBefore)
    {
        throw std::runtime_error("trace changed while replaying data writes");
    }
    uint64_t const targetTableBytesAfter =
        fs::file_size(options.DataWriteTargets);
    fs::file_time_type const targetTableWriteAfter =
        fs::last_write_time(options.DataWriteTargets);
    if (targetTableBytesAfter != targetTableBytesBefore ||
        targetTableWriteAfter != targetTableWriteBefore)
    {
        throw std::runtime_error(
            "data-write target table changed while replaying");
    }

    bool const replayComplete =
        replayAccounting.StopReason == EventType::Position &&
        PositionEquals(finalPosition, requestedTo);
    bool const exactReplayWindow =
        PositionEquals(actualFrom, requestedFrom) &&
        PositionEquals(finalPosition, requestedTo);
    bool expectationsPassed = true;
    auto const& targetsAfter = recorder.Targets();
    auto const& counts = recorder.TargetCounts();
    for (size_t index = 0; index < targetsAfter.size(); ++index)
    {
        expectationsPassed =
            expectationsPassed &&
            ExpectedCountMatches(
                targetsAfter[index].ExpectedOverwriteCount,
                counts[index].Overwrites) &&
            ExpectedCountMatches(
                targetsAfter[index].ExpectedWriteCount,
                counts[index].Writes);
    }
    bool const snapshotQueriesValid =
        std::all_of(
            initialImages.begin(),
            initialImages.end(),
            [&actualFrom](DataWriteMemoryImage const& image)
            {
                return image.QueryValid &&
                    PositionEquals(
                        image.ObservationPosition,
                        actualFrom);
            }) &&
        std::all_of(
            finalImages.begin(),
            finalImages.end(),
            [&finalPosition](DataWriteMemoryImage const& image)
            {
                return image.QueryValid &&
                    PositionEquals(
                        image.ObservationPosition,
                        finalPosition);
            });
    std::vector<DataWriteTargetEvidence> targetEvidence;
    targetEvidence.reserve(targetsAfter.size());
    for (size_t index = 0; index < targetsAfter.size(); ++index)
    {
        targetEvidence.push_back(
            EvaluateDataWriteTargetEvidence(
                index,
                targetsAfter,
                counts,
                recorder.Events(),
                recorder.Pairs(),
                initialImages,
                finalImages));
    }
    bool const targetEvidencePassed = std::all_of(
        targetEvidence.begin(),
        targetEvidence.end(),
        [](DataWriteTargetEvidence const& evidence)
        {
            return evidence.Passed;
        });
    bool const replayCountersSane =
        replayAccounting.StepsExecuted != 0 &&
        replayAccounting.InstructionsExecuted <= replayAccounting.StepsExecuted;
    bool const collectorChecksPassed =
        replayComplete &&
        exactReplayWindow &&
        expectationsPassed &&
        targetEvidencePassed &&
        replayCountersSane &&
        DataWriteHistoryIsGapFree(
            recorder.NontrivialGapCount(),
            recorder.ContinuityBreakCount()) &&
        !recorder.Truncated() &&
        !recorder.CallbackFailed() &&
        recorder.AmbiguousCallbacks() == 0 &&
        recorder.OrderingValid() &&
        recorder.ContextsValid() &&
        recorder.PairingValid() &&
        recorder.PairingComplete();

    WriteDataWritesJsonl(
        options,
        traceBytesBefore,
        targetTableBytesBefore,
        selected,
        *ownedEngine,
        requestedFrom,
        requestedTo,
        actualFrom,
        replayAccounting,
        finalPosition,
        recorder,
        initialImages,
        finalImages,
        targetEvidence,
        gapStatistics,
        replayComplete,
        exactReplayWindow,
        expectationsPassed,
        snapshotQueriesValid,
        targetEvidencePassed,
        replayCountersSane,
        collectorChecksPassed);

    char const* const stopReason =
        GetEventTypeName(replayAccounting.StopReason);
    std::cerr
        << "data-write complete; targets=" << targetsAfter.size()
        << " events=" << recorder.Events().size()
        << " pairs=" << recorder.Pairs().size()
        << " callbacks=" << recorder.CallbackHits()
        << " ambiguous=" << recorder.AmbiguousCallbacks()
        << " truncated=" << (recorder.Truncated() ? "true" : "false")
        << " stop=" << (stopReason == nullptr ? "" : stopReason)
        << " replayComplete=" << (replayComplete ? "true" : "false")
        << " exactWindow=" << (exactReplayWindow ? "pass" : "fail")
        << " expectations=" << (expectationsPassed ? "pass" : "fail")
        << " snapshotQueries=" << (snapshotQueriesValid ? "pass" : "fail")
        << " targetEvidence=" << (targetEvidencePassed ? "pass" : "fail")
        << " pairing="
        << (recorder.PairingValid() && recorder.PairingComplete()
                ? "pass"
                : "fail")
        << " collectorChecks=" << (collectorChecksPassed ? "pass" : "fail")
        << "\n";
    return collectorChecksPassed ? 0 : 10;
}

int AnalyzeCallContext(Options const& options)
{
    uint64_t const traceBytesBefore = fs::file_size(options.Trace);
    fs::file_time_type const traceWriteBefore = fs::last_write_time(options.Trace);
    uint64_t const targetTableBytesBefore =
        fs::file_size(options.CallContextTargets);
    fs::file_time_type const targetTableWriteBefore =
        fs::last_write_time(options.CallContextTargets);

    auto [ownedEngine, createResult] = MakeReplayEngine();
    if (createResult != 0 || !ownedEngine)
    {
        std::cerr << "CreateReplayEngine failed: " << createResult << "\n";
        return 3;
    }
    if (!ownedEngine->Initialize(options.Trace.c_str()))
    {
        std::cerr << "IReplayEngine::Initialize failed\n";
        return 3;
    }

    SelectedModule const selected = SelectModule(*ownedEngine, options);
    Module const& module = *selected.ModuleValue;
    ModuleInstance const& instance = *selected.Instance;
    uint64_t const base = static_cast<uint64_t>(module.Address);
    if (module.Size == 0 ||
        module.Size > options.MaxModuleBytes ||
        module.Size > std::numeric_limits<uint64_t>::max() - base ||
        base > std::numeric_limits<uint32_t>::max() ||
        base + module.Size > uint64_t{1} + std::numeric_limits<uint32_t>::max())
    {
        throw std::runtime_error(
            "selected module is not a bounded 32-bit call-context target");
    }
    if (ownedEngine->GetSystemInfo().System.ProcessorArchitecture !=
        PROCESSOR_ARCHITECTURE_INTEL)
    {
        throw std::runtime_error(
            "call-context mode requires an x86 trace");
    }

    PositionRange const& lifetime = ownedEngine->GetLifetime();
    Position const requestedFrom = options.From.value_or(lifetime.Min);
    Position const requestedTo = options.To.value_or(lifetime.Max);
    Position const replayLimit = options.To.value_or(Position::Max);
    if (requestedFrom < lifetime.Min ||
        requestedFrom > lifetime.Max ||
        requestedTo < lifetime.Min ||
        requestedTo > lifetime.Max ||
        requestedFrom > requestedTo)
    {
        throw std::runtime_error(
            "requested replay window lies outside trace lifetime");
    }
    if (requestedFrom.Sequence < instance.LoadTime ||
        (instance.UnloadTime != TTD::SequenceId::Max &&
         requestedTo.Sequence >= instance.UnloadTime))
    {
        throw std::runtime_error(
            "selected module is not active for the complete requested window");
    }

    std::vector<CallContextTarget> targets =
        ReadCallContextTargets(options.CallContextTargets);
    GapStatistics gapStatistics;
    CallContextRecorder recorder(
        base,
        module.Size,
        std::move(targets),
        options.CallContextStackBytes,
        options.CallContextEventLimit,
        gapStatistics);
    UniqueCursor cursor{ownedEngine->NewCursor()};
    if (!cursor)
    {
        throw std::runtime_error("IReplayEngine::NewCursor failed");
    }
    cursor->SetReplayFlags(
        ReplayFlags::ReplayAllSegmentsWithoutFiltering |
        ReplayFlags::ReplaySegmentsSequentially);
    for (CallContextTarget const& target : recorder.Targets())
    {
        bool const added = cursor->AddMemoryWatchpoint(
            MemoryWatchpointData
            {
                .Address = static_cast<TTD::GuestAddress>(base + target.EntryRva),
                .Size = 1,
                .AccessMask = DataAccessMask::Execute,
            });
        if (!added)
        {
            throw std::runtime_error(
                "AddMemoryWatchpoint failed for call-context target entry " +
                Hex(target.EntryRva));
        }
    }
    cursor->SetMemoryWatchpointCallback(
        CallContextEntryCallback,
        reinterpret_cast<uintptr_t>(&recorder));
    cursor->SetCallReturnCallback(
        CallContextCallReturnCallback,
        reinterpret_cast<uintptr_t>(&recorder));
    cursor->SetThreadContinuityBreakCallback(
        CallContextContinuityBreakCallback,
        reinterpret_cast<uintptr_t>(&recorder));
    cursor->SetGapKindMask(GapKindMask::All);
    cursor->SetGapEventMask(GapEventMask::All);
    cursor->SetGapEventCallback(
        CallContextGapCallback,
        reinterpret_cast<uintptr_t>(&recorder));
    cursor->SetEventMask(EventMask::MemoryWatchpoint | EventMask::Gap);
    cursor->SetPosition(requestedFrom);

    std::cerr
        << "replaying call-context trace; module="
        << ToUtf8(std::wstring(module.pName, module.NameLength))
        << " base=" << Hex(base)
        << " size=" << Hex(module.Size)
        << " targets=" << recorder.Targets().size()
        << " from=" << PositionString(requestedFrom)
        << " to=" << PositionString(requestedTo)
        << " mode=sequential\n";
    ReplayAccounting const replayAccounting = AccumulateReplayChunks(
        [&cursor, &replayLimit]()
        {
            return cursor->ReplayForward(
                replayLimit,
                static_cast<StepCount>(kReplayChunkSteps));
        });
    Position const finalPosition = cursor->GetPosition();

    uint64_t const traceBytesAfter = fs::file_size(options.Trace);
    fs::file_time_type const traceWriteAfter = fs::last_write_time(options.Trace);
    if (traceBytesAfter != traceBytesBefore || traceWriteAfter != traceWriteBefore)
    {
        throw std::runtime_error("trace changed while replaying call context");
    }
    uint64_t const targetTableBytesAfter =
        fs::file_size(options.CallContextTargets);
    fs::file_time_type const targetTableWriteAfter =
        fs::last_write_time(options.CallContextTargets);
    if (targetTableBytesAfter != targetTableBytesBefore ||
        targetTableWriteAfter != targetTableWriteBefore)
    {
        throw std::runtime_error(
            "call-context target table changed while replaying");
    }

    bool const terminalReasonPassed =
        !options.To
            ? replayAccounting.StopReason == EventType::Process
            : replayAccounting.StopReason == EventType::Position;
    bool const replayComplete =
        terminalReasonPassed && finalPosition >= requestedTo;
    bool expectationsPassed = true;
    auto const& targetsAfter = recorder.Targets();
    auto const& counts = recorder.TargetCounts();
    for (size_t index = 0; index < targetsAfter.size(); ++index)
    {
        expectationsPassed =
            expectationsPassed &&
            ExpectedCountMatches(
                targetsAfter[index].ExpectedEntryCount,
                counts[index].Entries) &&
            ExpectedCountMatches(
                targetsAfter[index].ExpectedCallCount,
                counts[index].Calls) &&
            ExpectedCountMatches(
                targetsAfter[index].ExpectedReturnCount,
                counts[index].Returns);
    }

    std::vector<uint64_t> matchedCallEntries(targetsAfter.size(), 0);
    for (CallContextInvocation const& invocation : recorder.Invocations())
    {
        if (invocation.CallEntryChecksPassed)
        {
            ++matchedCallEntries[invocation.TargetIndex];
        }
    }
    bool pairingExpectationsPassed = true;
    for (size_t index = 0; index < targetsAfter.size(); ++index)
    {
        CallContextTarget const& target = targetsAfter[index];
        if (target.ExpectedCallCount && target.ExpectedEntryCount &&
            *target.ExpectedCallCount == *target.ExpectedEntryCount)
        {
            pairingExpectationsPassed =
                pairingExpectationsPassed &&
                matchedCallEntries[index] == *target.ExpectedCallCount;
        }
    }

    // In call-context mode callback classes can overlap in ways that make the
    // coverage collector's callback_hits <= instructions invariant inapplicable.
    // Keep only the replay engine's own instructions <= steps sanity check.
    bool const replayCountersSane =
        replayAccounting.InstructionsExecuted <= replayAccounting.StepsExecuted;
    bool const collectorChecksPassed =
        replayComplete &&
        expectationsPassed &&
        pairingExpectationsPassed &&
        replayCountersSane &&
        !recorder.Truncated() &&
        !recorder.CallbackFailed() &&
        recorder.OrderingValid() &&
        recorder.ContextsValid();

    WriteCallContextJsonl(
        options,
        traceBytesBefore,
        targetTableBytesBefore,
        selected,
        *ownedEngine,
        requestedFrom,
        requestedTo,
        replayAccounting,
        finalPosition,
        recorder,
        gapStatistics,
        replayComplete,
        expectationsPassed,
        pairingExpectationsPassed,
        replayCountersSane,
        collectorChecksPassed);

    char const* const stopReason =
        GetEventTypeName(replayAccounting.StopReason);
    std::cerr
        << "call-context complete; targets=" << targetsAfter.size()
        << " events=" << recorder.Events().size()
        << " invocations=" << recorder.Invocations().size()
        << " callReturnCallbacks=" << recorder.CallReturnCallbacks()
        << " entryCallbacks=" << recorder.EntryCallbacks()
        << " truncated=" << (recorder.Truncated() ? "true" : "false")
        << " stop=" << (stopReason == nullptr ? "" : stopReason)
        << " replayComplete=" << (replayComplete ? "true" : "false")
        << " expectations=" << (expectationsPassed ? "pass" : "fail")
        << " pairing=" << (pairingExpectationsPassed ? "pass" : "fail")
        << " collectorChecks=" << (collectorChecksPassed ? "pass" : "fail")
        << "\n";
    return collectorChecksPassed ? 0 : 10;
}

int Analyze(Options const& options)
{
    uint64_t const traceBytesBefore = fs::file_size(options.Trace);
    fs::file_time_type const traceWriteBefore = fs::last_write_time(options.Trace);

    auto [ownedEngine, createResult] = MakeReplayEngine();
    if (createResult != 0 || !ownedEngine)
    {
        std::cerr << "CreateReplayEngine failed: " << createResult << "\n";
        return 3;
    }
    if (!ownedEngine->Initialize(options.Trace.c_str()))
    {
        std::cerr << "IReplayEngine::Initialize failed\n";
        return 3;
    }

    SelectedModule const selected = SelectModule(*ownedEngine, options);
    Module const& module = *selected.ModuleValue;
    ModuleInstance const& instance = *selected.Instance;
    uint64_t const base = static_cast<uint64_t>(module.Address);
    if (module.Size == 0 ||
        module.Size > options.MaxModuleBytes ||
        module.Size > std::numeric_limits<uint64_t>::max() - base ||
        module.Size > std::numeric_limits<size_t>::max() - 63)
    {
        throw std::runtime_error("selected module has an unsafe coverage bitmap size");
    }

    PositionRange const& lifetime = ownedEngine->GetLifetime();
    Position const requestedFrom = options.From.value_or(lifetime.Min);
    Position const requestedTo = options.To.value_or(lifetime.Max);
    Position const replayLimit = options.To.value_or(Position::Max);
    if (requestedFrom < lifetime.Min ||
        requestedFrom > lifetime.Max ||
        requestedTo < lifetime.Min ||
        requestedTo > lifetime.Max ||
        requestedFrom > requestedTo)
    {
        throw std::runtime_error("requested replay window lies outside trace lifetime");
    }
    if (requestedFrom.Sequence < instance.LoadTime ||
        (instance.UnloadTime != TTD::SequenceId::Max &&
         requestedTo.Sequence >= instance.UnloadTime))
    {
        throw std::runtime_error(
            "selected module is not active for the complete requested window");
    }

    auto validateRva =
        [&](uint64_t rva, char const* option)
        {
            if (rva >= module.Size)
            {
                throw std::runtime_error(
                    std::string(option) +
                    " lies outside the selected module: " + Hex(rva));
            }
        };
    for (uint64_t const rva : options.MustHitRvas)
    {
        validateRva(rva, "--must-hit-rva");
    }
    for (uint64_t const rva : options.MustMissRvas)
    {
        validateRva(rva, "--must-miss-rva");
    }

    AtomicCoverage coverage(base, module.Size);
    GapStatistics gapStatistics;
    UniqueCursor cursor{ownedEngine->NewCursor()};
    if (!cursor)
    {
        throw std::runtime_error("IReplayEngine::NewCursor failed");
    }

    ReplayFlags replayFlags = ReplayFlags::ReplayAllSegmentsWithoutFiltering;
    if (options.Sequential)
    {
        replayFlags |= ReplayFlags::ReplaySegmentsSequentially;
    }
    cursor->SetReplayFlags(replayFlags);
    bool const watchpointAdded = cursor->AddMemoryWatchpoint(
        MemoryWatchpointData
        {
            .Address = module.Address,
            .Size = module.Size,
            .AccessMask = DataAccessMask::Execute,
        });
    if (!watchpointAdded)
    {
        throw std::runtime_error("AddMemoryWatchpoint failed");
    }
    cursor->SetMemoryWatchpointCallback(
        ExecuteCallback,
        reinterpret_cast<uintptr_t>(&coverage));
    cursor->SetGapKindMask(GapKindMask::All);
    cursor->SetGapEventMask(GapEventMask::All);
    cursor->SetGapEventCallback(
        GapCallback,
        reinterpret_cast<uintptr_t>(&gapStatistics));
    cursor->SetEventMask(EventMask::MemoryWatchpoint | EventMask::Gap);
    cursor->SetPosition(requestedFrom);

    std::cerr
        << "replaying trace; module="
        << ToUtf8(std::wstring(module.pName, module.NameLength))
        << " base=" << Hex(base)
        << " size=" << Hex(module.Size)
        << " from=" << PositionString(requestedFrom)
        << " to=" << PositionString(requestedTo)
        << "\n";
    ReplayAccounting const replayAccounting = AccumulateReplayChunks(
        [&cursor, &replayLimit]()
        {
            return cursor->ReplayForward(
                replayLimit,
                static_cast<StepCount>(kReplayChunkSteps));
        });
    Position const finalPosition = cursor->GetPosition();
    std::vector<Range> const ranges = coverage.Ranges();

    uint64_t const traceBytesAfter = fs::file_size(options.Trace);
    fs::file_time_type const traceWriteAfter = fs::last_write_time(options.Trace);
    if (traceBytesAfter != traceBytesBefore || traceWriteAfter != traceWriteBefore)
    {
        throw std::runtime_error("trace changed while replaying");
    }

    bool const terminalReasonPassed =
        !options.To
            ? replayAccounting.StopReason == EventType::Process
            : replayAccounting.StopReason == EventType::Position;
    bool const replayComplete =
        terminalReasonPassed &&
        finalPosition >= requestedTo;
    bool markerAssertionsPassed = true;
    for (uint64_t const rva : options.MustHitRvas)
    {
        markerAssertionsPassed =
            markerAssertionsPassed && coverage.IsCovered(rva);
    }
    for (uint64_t const rva : options.MustMissRvas)
    {
        markerAssertionsPassed =
            markerAssertionsPassed && !coverage.IsCovered(rva);
    }
    bool const collectorChecksPassed =
        replayComplete && markerAssertionsPassed;

    // A watchpoint hit requires an executed instruction, and an instruction is
    // a step, so callback_hits <= instructions_executed <= steps_executed is a
    // hard invariant.  It is exactly the invariant the pre-fix collector broke
    // by publishing a truncated step count, so refuse to publish rather than
    // emit another receipt that lies quietly.
    uint64_t const callbackHits = coverage.CallbackHits();
    bool const countersQuarantined =
        !CountersAreConsistent(
            callbackHits,
            replayAccounting.InstructionsExecuted,
            replayAccounting.StepsExecuted);
    if (countersQuarantined)
    {
        char const* const failedStopReason =
            GetEventTypeName(replayAccounting.StopReason);
        std::string const detail =
            "callback_hits=" + std::to_string(callbackHits) +
            " instructions_executed=" +
            std::to_string(replayAccounting.InstructionsExecuted) +
            " steps_executed=" +
            std::to_string(replayAccounting.StepsExecuted) +
            " gap_events=" + std::to_string(gapStatistics.Total()) +
            " chunks=" + std::to_string(replayAccounting.ChunkCount) +
            " stop_reason=" +
            (failedStopReason == nullptr ? "" : failedStopReason) +
            " final_position=" + PositionString(finalPosition);
        if (!options.QuarantineCounters)
        {
            throw std::runtime_error(
                "replay accounting is impossible; refusing to publish "
                "coverage: " + detail);
        }
        std::cerr
            << "replay accounting is impossible; publishing coverage with the "
               "counters quarantined (--quarantine-counters): "
            << detail << "\n";
    }

    WriteJsonl(
        options,
        traceBytesBefore,
        selected,
        *ownedEngine,
        requestedFrom,
        requestedTo,
        replayAccounting,
        finalPosition,
        coverage,
        gapStatistics,
        ranges,
        replayComplete,
        markerAssertionsPassed,
        collectorChecksPassed,
        countersQuarantined);

    char const* const stopReason =
        GetEventTypeName(replayAccounting.StopReason);
    std::cerr << "complete; ranges=" << ranges.size()
              << " callbacks=" << callbackHits
              << " steps=" << replayAccounting.StepsExecuted
              << " instructions=" << replayAccounting.InstructionsExecuted
              << " chunks=" << replayAccounting.ChunkCount
              << " countersQuarantined="
              << (countersQuarantined ? "true" : "false")
              << " stop=" << (stopReason == nullptr ? "" : stopReason)
              << " replayComplete=" << (replayComplete ? "true" : "false")
              << " markerAssertions="
              << (markerAssertionsPassed ? "pass" : "fail")
              << " collectorChecks="
              << (collectorChecksPassed ? "pass" : "fail")
              << "\n";
    if (!collectorChecksPassed)
    {
        return 10;
    }
    // Publishing with quarantined counters is not a clean pass.  The caller
    // gets the ranges and a distinct, loud exit code.
    return countersQuarantined ? 11 : 0;
}
} // namespace

int wmain(int argc, wchar_t* argv[])
{
    try
    {
        Options const options = ParseOptions(argc, argv);
        if (options.SelfTest)
        {
            return RunSelfTests() ? 0 : 2;
        }
        switch (options.Mode)
        {
        case AnalysisMode::CallContext:
            return AnalyzeCallContext(options);
        case AnalysisMode::DataWrites:
            return AnalyzeDataWrites(options);
        case AnalysisMode::Coverage:
        default:
            return Analyze(options);
        }
    }
    catch (std::exception const& error)
    {
        std::cerr << "error: " << error.what() << "\n";
        PrintUsage();
        return 2;
    }
}
