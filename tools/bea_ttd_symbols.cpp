// Session-local Ghidra-name loader for x86 CDB/WinDbg/TTD.
//
// Build with Build-BeaTtdSymbols.ps1, then in a debugger session:
//   .load C:\...\bea_ttd_symbols.dll
//   !beasym C:\...\bea-symbol-map.tsv BEA
//
// The map contains RVAs.  This extension resolves the live/replay module base,
// bounds-checks every row against the loaded module, and uses
// IDebugSymbols3::AddSyntheticSymbol.  It changes only the debugger session.

#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <dbgeng.h>

#include <cerrno>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <limits>
#include <sstream>
#include <string>
#include <vector>

namespace {

std::vector<std::string> split_command_line(PCSTR raw) {
    std::vector<std::string> result;
    std::string current;
    bool quoted = false;
    for (const char* cursor = raw == nullptr ? "" : raw; *cursor != '\0'; ++cursor) {
        const char value = *cursor;
        if (value == '"') {
            quoted = !quoted;
        } else if (!quoted && (value == ' ' || value == '\t')) {
            if (!current.empty()) {
                result.push_back(current);
                current.clear();
            }
        } else {
            current.push_back(value);
        }
    }
    if (!current.empty()) {
        result.push_back(current);
    }
    return result;
}

std::vector<std::string> split_tabs(const std::string& line) {
    std::vector<std::string> result;
    std::size_t start = 0;
    while (true) {
        const std::size_t separator = line.find('\t', start);
        if (separator == std::string::npos) {
            result.push_back(line.substr(start));
            break;
        }
        result.push_back(line.substr(start, separator - start));
        start = separator + 1;
    }
    return result;
}

bool parse_u64(const std::string& text, std::uint64_t& result) {
    if (text.empty() || text.front() == '-') {
        return false;
    }
    errno = 0;
    char* end = nullptr;
    const unsigned long long value = _strtoui64(text.c_str(), &end, 0);
    if (errno != 0 || end == text.c_str() || *end != '\0') {
        return false;
    }
    result = static_cast<std::uint64_t>(value);
    return true;
}

void output(IDebugControl* control, ULONG mask, const std::string& text) {
    control->Output(mask, "%s", text.c_str());
}

struct InterfaceGuard {
    IUnknown* value = nullptr;
    ~InterfaceGuard() {
        if (value != nullptr) {
            value->Release();
        }
    }
};

struct PendingSymbol {
    std::size_t row = 0;
    std::uint64_t rva = 0;
    ULONG size = 0;
    std::string name;
    HRESULT firstStatus = S_OK;
};

}  // namespace

extern "C" HRESULT CALLBACK DebugExtensionInitialize(PULONG version, PULONG flags) {
    *version = DEBUG_EXTENSION_VERSION(1, 0);
    *flags = 0;
    return S_OK;
}

extern "C" void CALLBACK DebugExtensionUninitialize() {
}

extern "C" HRESULT CALLBACK beahelp(PDEBUG_CLIENT client, PCSTR) {
    IDebugControl* control = nullptr;
    if (FAILED(client->QueryInterface(__uuidof(IDebugControl), reinterpret_cast<void**>(&control)))) {
        return E_NOINTERFACE;
    }
    InterfaceGuard controlGuard{control};
    output(
        control,
        DEBUG_OUTPUT_NORMAL,
        "BEA synthetic symbols v1\n"
        "  !beasym <symbol-map.tsv> [module]\n"
        "Example:\n"
        "  !beasym C:\\lab\\bea-symbol-map.tsv BEA\n"
        "Rows are module-relative, bounds checked, and session-local.\n"
    );
    return S_OK;
}

extern "C" HRESULT CALLBACK beasym(PDEBUG_CLIENT client, PCSTR args) {
    IDebugControl* control = nullptr;
    IDebugSymbols3* symbols = nullptr;
    if (FAILED(client->QueryInterface(__uuidof(IDebugControl), reinterpret_cast<void**>(&control)))) {
        return E_NOINTERFACE;
    }
    InterfaceGuard controlGuard{control};
    if (FAILED(client->QueryInterface(__uuidof(IDebugSymbols3), reinterpret_cast<void**>(&symbols)))) {
        output(control, DEBUG_OUTPUT_ERROR, "BEASYM_ERROR IDebugSymbols3 is unavailable\n");
        return E_NOINTERFACE;
    }
    InterfaceGuard symbolsGuard{symbols};

    const std::vector<std::string> tokens = split_command_line(args);
    if (tokens.empty() || tokens.size() > 2) {
        output(
            control,
            DEBUG_OUTPUT_ERROR,
            "BEASYM_ERROR usage: !beasym <symbol-map.tsv> [module]\n"
        );
        return E_INVALIDARG;
    }
    const std::string mapPath = tokens[0];
    const std::string moduleName = tokens.size() == 2 ? tokens[1] : "BEA";

    ULONG moduleIndex = 0;
    ULONG64 moduleBase = 0;
    HRESULT status = symbols->GetModuleByModuleName(
        moduleName.c_str(), 0, &moduleIndex, &moduleBase
    );
    if (FAILED(status)) {
        std::ostringstream message;
        message << "BEASYM_ERROR module='" << moduleName
                << "' GetModuleByModuleName=0x" << std::hex
                << static_cast<unsigned long>(status) << "\n";
        output(control, DEBUG_OUTPUT_ERROR, message.str());
        return status;
    }

    DEBUG_MODULE_PARAMETERS parameters = {};
    status = symbols->GetModuleParameters(1, &moduleBase, 0, &parameters);
    if (FAILED(status) || parameters.Size == 0) {
        output(
            control,
            DEBUG_OUTPUT_ERROR,
            "BEASYM_ERROR unable to determine a non-zero module extent\n"
        );
        return FAILED(status) ? status : E_FAIL;
    }

    std::ifstream input(mapPath, std::ios::binary);
    if (!input) {
        output(
            control,
            DEBUG_OUTPUT_ERROR,
            "BEASYM_ERROR cannot open map='" + mapPath + "'\n"
        );
        return HRESULT_FROM_WIN32(ERROR_FILE_NOT_FOUND);
    }

    std::size_t rows = 0;
    std::size_t added = 0;
    std::size_t malformed = 0;
    std::size_t outOfModule = 0;
    std::size_t rejected = 0;
    std::size_t retryRecovered = 0;
    std::vector<PendingSymbol> pending;
    std::string line;
    while (std::getline(input, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.empty() || line.front() == '#' || line.rfind("rva\t", 0) == 0) {
            continue;
        }
        rows++;
        const std::vector<std::string> columns = split_tabs(line);
        if (columns.size() < 3) {
            std::ostringstream message;
            message << "BEASYM_MALFORMED row=" << rows
                    << " reason=columns\n";
            output(control, DEBUG_OUTPUT_ERROR, message.str());
            malformed++;
            continue;
        }
        std::uint64_t rva = 0;
        std::uint64_t requestedSize = 0;
        if (!parse_u64(columns[0], rva) || !parse_u64(columns[1], requestedSize) ||
            columns[2].empty()) {
            std::ostringstream message;
            message << "BEASYM_MALFORMED row=" << rows
                    << " reason=fields\n";
            output(control, DEBUG_OUTPUT_ERROR, message.str());
            malformed++;
            continue;
        }
        if (requestedSize == 0) {
            std::ostringstream message;
            message << "BEASYM_MALFORMED row=" << rows
                    << " rva=0x" << std::hex << rva
                    << std::dec << " name=\"" << columns[2]
                    << "\" reason=zero-size\n";
            output(control, DEBUG_OUTPUT_ERROR, message.str());
            malformed++;
            continue;
        }
        if (rva >= parameters.Size) {
            std::ostringstream message;
            message << "BEASYM_OUT_OF_MODULE row=" << rows
                    << " rva=0x" << std::hex << rva
                    << " moduleSize=0x" << parameters.Size
                    << std::dec << " name=\"" << columns[2] << "\"\n";
            output(control, DEBUG_OUTPUT_ERROR, message.str());
            outOfModule++;
            continue;
        }
        const std::uint64_t remaining = static_cast<std::uint64_t>(parameters.Size) - rva;
        if (requestedSize > remaining) {
            std::ostringstream message;
            message << "BEASYM_OUT_OF_MODULE row=" << rows
                    << " rva=0x" << std::hex << rva
                    << " size=0x" << requestedSize
                    << " moduleSize=0x" << parameters.Size
                    << std::dec << " name=\"" << columns[2]
                    << "\" reason=range\n";
            output(control, DEBUG_OUTPUT_ERROR, message.str());
            outOfModule++;
            continue;
        }
        const std::uint64_t boundedSize = requestedSize;
        const ULONG symbolSize = static_cast<ULONG>(
            boundedSize > std::numeric_limits<ULONG>::max()
                ? std::numeric_limits<ULONG>::max()
                : boundedSize
        );
        DEBUG_MODULE_AND_ID id = {};
        status = symbols->AddSyntheticSymbol(
            moduleBase + rva,
            symbolSize,
            columns[2].c_str(),
            DEBUG_ADDSYNTHSYM_DEFAULT,
            &id
        );
        if (SUCCEEDED(status)) {
            added++;
        } else {
            pending.push_back(PendingSymbol{
                rows,
                rva,
                symbolSize,
                columns[2],
                status,
            });
        }
    }

    // DbgEng can reject the first AddSyntheticSymbol call with
    // ERROR_MOD_NOT_FOUND while it lazily initializes the module's synthetic
    // symbol owner. Retrying only failed rows after at least one successful add
    // distinguishes that one-time engine state from a persistent bad row.
    for (const PendingSymbol& item : pending) {
        DEBUG_MODULE_AND_ID id = {};
        status = symbols->AddSyntheticSymbol(
            moduleBase + item.rva,
            item.size,
            item.name.c_str(),
            DEBUG_ADDSYNTHSYM_DEFAULT,
            &id
        );
        std::ostringstream message;
        if (SUCCEEDED(status)) {
            added++;
            retryRecovered++;
            message << "BEASYM_RETRY_OK row=" << item.row
                    << " rva=0x" << std::hex << item.rva
                    << " size=0x" << item.size
                    << " firstHresult=0x"
                    << static_cast<unsigned long>(item.firstStatus)
                    << std::dec << " name=\"" << item.name << "\"\n";
            output(control, DEBUG_OUTPUT_NORMAL, message.str());
        } else {
            rejected++;
            message << "BEASYM_REJECT row=" << item.row
                    << " rva=0x" << std::hex << item.rva
                    << " size=0x" << item.size
                    << " firstHresult=0x"
                    << static_cast<unsigned long>(item.firstStatus)
                    << " retryHresult=0x"
                    << static_cast<unsigned long>(status)
                    << std::dec << " name=\"" << item.name << "\"\n";
            output(control, DEBUG_OUTPUT_ERROR, message.str());
        }
    }

    std::ostringstream summary;
    summary << "BEASYM_OK module=" << moduleName
            << " base=0x" << std::hex << moduleBase
            << " size=0x" << parameters.Size
             << std::dec << " rows=" << rows
             << " added=" << added
             << " retryRecovered=" << retryRecovered
             << " rejected=" << rejected
            << " malformed=" << malformed
            << " outOfModule=" << outOfModule
            << " map=\"" << mapPath << "\"\n";
    output(control, DEBUG_OUTPUT_NORMAL, summary.str());
    return (rejected == 0 && malformed == 0 && outOfModule == 0) ? S_OK : S_FALSE;
}
