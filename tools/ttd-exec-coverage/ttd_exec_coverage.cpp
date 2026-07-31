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
#include <memory>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <vector>

namespace
{
using namespace TTD::Replay;
namespace fs = std::filesystem;

constexpr char const* kSchema = "bea.ttd.exec-coverage.v1";
constexpr uint64_t kDefaultMaxModuleBytes = 1ull << 30;

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

    std::cout
        << "self-test: 9/9 coalescing and 6/6 bitmap groups passed; "
        << "containment, clipping, boundaries, randomized parity, and "
        << "concurrent atomic OR are preserved\n"
        << "self-test: 6/6 replay-accounting groups passed; chunked totals "
        << "cross 2^32 in 64 bits, non-advancing or impossible chunks fail "
        << "closed, and both recorded impossible counter triples are "
        << "rejected while the healthy one is accepted\n";
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

struct Options
{
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
};

void PrintUsage()
{
    std::cerr
        << "Usage:\n"
        << "  ttd_exec_coverage --self-test\n"
        << "  ttd_exec_coverage --trace FILE --module NAME --out FILE\n"
        << "    --expect-size NUMBER --expect-timestamp NUMBER"
        << " --expect-checksum NUMBER [options]\n\n"
        << "Options:\n"
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
        << "  --must-miss-rva NUMBER     (repeatable)\n";
}

Options ParseOptions(int argc, wchar_t* argv[])
{
    Options options;
    bool maxModuleBytesSet = false;

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
        return Analyze(options);
    }
    catch (std::exception const& error)
    {
        std::cerr << "error: " << error.what() << "\n";
        PrintUsage();
        return 2;
    }
}
