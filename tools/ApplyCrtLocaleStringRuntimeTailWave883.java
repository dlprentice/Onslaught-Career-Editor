//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtLocaleStringRuntimeTailWave883 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String[] previousNames, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crt-locale-string-runtime-tail-wave883",
            "wave883-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-crt-runtime-infrastructure",
            "high-importance-low-local-evidence-density",
            "compiler-runtime",
            "crt-runtime",
            "raw-commentless-tail"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        String actualSignature = readBack.getSignature().toString();
        if (!actualSignature.equals(spec.signature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature);
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!nameAllowed(fn.getName(), spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.signature);
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00563ad3",
                "CRT__FpuTransDispatch2_ClearStatusAndHandle",
                new String[] {},
                "void CRT__FpuTransDispatch2_ClearStatusAndHandle(void)",
                "Wave883 static read-back: raw commentless head reached from __ctrandisp2 and __ctrandisp1. Decompile clears the EBP-0x2c8 low bit, checks DAT_009d08b4, classifies exponent/status cases including 0x7ff0 and in_FPUStatusWord bit 0x20, writes the exception payload at EBP-0x8e..EBP-0x76, then calls CRT__HandleFloatingPointException. Static retail Ghidra evidence only; exact CRT version identity, hidden frame layout, runtime FP exception behavior, and rebuild parity remain unproven.",
                tags("fpu-runtime", "math-exception-runtime", "raw-commentless-head")
            ),
            new Spec(
                "0x00565ee0",
                "CRT__LCMapStringA_Compat",
                new String[] {},
                "int CRT__LCMapStringA_Compat(void)",
                "Wave883 static read-back: LCMapStringA/W compatibility adapter. It probes LCMapStringW versus LCMapStringA support into DAT_009d09b0, trims positive source length with CRT__StrNLen, uses MultiByteToWideChar, LCMapStringW, WideCharToMultiByte, alloca guard calls, and flags 0x220/0x400. Xrefs include CRT__ToLowerWithLocale, CRT__ToUpperWithLocale, CRT__MbsIcmp_LocaleLock, CDXTexture__AsciiToLowerInPlace, and CRT__BuildMultibyteCTypeCaseTables_005681e5. Static evidence only; exact Windows NLS runtime behavior remains unproven.",
                tags("locale-runtime", "string-runtime", "nls-runtime")
            ),
            new Spec(
                "0x00567aa8",
                "CRT__GetErrnoThreadPtr_00567aa8",
                new String[] {},
                "int CRT__GetErrnoThreadPtr_00567aa8(void)",
                "Wave883 static read-back: returns CRT__GetOrInitThreadLocalRecord() + 0x8, the errno pointer slot. The row has 43 xrefs from CRT file-descriptor, Win32 file wrapper, spawn/open, strtol, and floating-point status paths including CRT__SetErrnoAndDosErrnoFromWinError and CRT__StrToLongWithBaseAndLocaleCType. Static evidence only; exact CRT TLS record layout remains unproven.",
                tags("errno-runtime", "thread-local-runtime", "file-descriptor-runtime")
            ),
            new Spec(
                "0x00567ab1",
                "CRT__GetDosErrnoThreadPtr_00567ab1",
                new String[] {},
                "int CRT__GetDosErrnoThreadPtr_00567ab1(void)",
                "Wave883 static read-back: returns CRT__GetOrInitThreadLocalRecord() + 0xc, the DOS errno pointer slot. The row has 21 xrefs from close/read/write/lseek/open/spawn/commit file-handle paths and CRT__SetErrnoAndDosErrnoFromWinError. Static evidence only; exact CRT TLS record layout remains unproven.",
                tags("errno-runtime", "thread-local-runtime", "file-descriptor-runtime")
            ),
            new Spec(
                "0x00567ed0",
                "CRT__SystemTimeToUnixTimestampLocal",
                new String[] {},
                "int CRT__SystemTimeToUnixTimestampLocal(void)",
                "Wave883 static read-back: ___timet_from_ft caller converts broken-down local time fields to a Unix-style timestamp. Decompile bounds years around 0x76c, uses month/day table DAT_00656a6c, calls CRT__EnsureTzsetInitialized, folds in DAT_00656988 timezone bias and 0x7c558180 epoch offset, and optionally applies _DAT_00656990 after CRT__IsInDst_WrapperLocked. Static evidence only; exact calendar/DST runtime behavior remains unproven.",
                tags("time-runtime", "timezone-runtime")
            ),
            new Spec(
                "0x005681bc",
                "CRT__ResetMultibyteTables_005681bc",
                new String[] {},
                "void CRT__ResetMultibyteTables_005681bc(void)",
                "Wave883 static read-back: CRT__SetMultibyteCodePage target clears 0x40 dwords at DAT_009d34c0, writes the trailing zero byte, and resets codepage/multibyte globals DAT_009d33a4, DAT_009d33bc, DAT_009d35c4, DAT_009d33b0, DAT_009d33b4, and DAT_009d33b8. Static evidence only; exact table schema remains unproven.",
                tags("multibyte-runtime", "ctype-runtime")
            ),
            new Spec(
                "0x005681e5",
                "CRT__BuildMultibyteCTypeCaseTables_005681e5",
                new String[] {},
                "void CRT__BuildMultibyteCTypeCaseTables_005681e5(void)",
                "Wave883 static read-back: CRT__SetMultibyteCodePage target builds multibyte ctype/case tables. It calls GetCPInfo(DAT_009d33a4), marks lead-byte ranges, calls CRT__GetStringTypeACompat and CRT__LCMapStringA_Compat twice, then fills DAT_009d34c0 and DAT_009d33c0 with uppercase/lowercase mapping flags; fallback ASCII path handles A-Z/a-z directly. Static evidence only; exact table schema and codepage behavior remain unproven.",
                tags("multibyte-runtime", "ctype-runtime", "locale-runtime")
            ),
            new Spec(
                "0x0056836a",
                "CRT__EnsureRuntimeInitSentinelSet",
                new String[] {},
                "void CRT__EnsureRuntimeInitSentinelSet(void)",
                "Wave883 static read-back: command-line/environment/argv setup helper checks DAT_009d4608 and, when unset, calls CRT__SetMultibyteCodePage(-3) before setting DAT_009d4608 to 1. Xrefs include CRT__ParseCommandLineToken, CRT__BuildEnvironTable, and CRT__BuildArgvTable. Static evidence only; exact startup ordering remains unproven.",
                tags("startup-runtime", "multibyte-runtime")
            ),
            new Spec(
                "0x00568390",
                "stricmp",
                new String[] {},
                "int __cdecl stricmp(char * a, char * b)",
                "Wave883 static read-back: case-insensitive string compare with 217 xrefs, including CLIParams__ParseCommandLine, CConsole__RegisterCommand, CDXMemBuffer helpers, and CSoundManager__ReloadLanguageSampleBank. ASCII path folds A-Z/a-z locally when DAT_009d0998 is zero; locale path uses CRT__ToLowerWithLocale with lock/index 0x13 bookkeeping. Static evidence only; exact locale collation behavior remains unproven.",
                tags("string-runtime", "locale-runtime", "widely-referenced-runtime")
            ),
            new Spec(
                "0x0056a1cd",
                "CRT__ParseFloatTextToLongDouble",
                new String[] {},
                "int CRT__ParseFloatTextToLongDouble(void)",
                "Wave883 static read-back: float text parser used by CRT__ParseFloatTextToFloatAndStatus, CRT__ParseFloatTextToFloat32, and CRT__ParseFloatTextToFloat64. Decompile shows whitespace/sign scanning, decimal separator DAT_00653aa0, state dispatch table 0x56a66e, digit classification via PTR_DAT_00653890 or CRT__GetCharTypeMask_Compat, and conversion helpers CRT__CollectMantissaDigits and CRT__ScaleDecimalMantissaToFloat10. Static evidence only; exact scanf/strtod compatibility remains unproven.",
                tags("float-parse-runtime", "locale-runtime")
            ),
            new Spec(
                "0x0056a69e",
                "CRT__GetStringTypeACompat",
                new String[] {},
                "int CRT__GetStringTypeACompat(void)",
                "Wave883 static read-back: GetStringTypeA/W compatibility adapter. It probes GetStringTypeW versus GetStringTypeA into DAT_009d0ad0, defaults codepage from DAT_009d09a8, converts through MultiByteToWideChar plus alloca/memset when the W path is available, otherwise calls GetStringTypeA with LCID from DAT_009d0998. Xrefs include CRT__GetCharTypeMask_Compat and ctype table builders. Static evidence only; exact Windows NLS behavior remains unproven.",
                tags("nls-runtime", "ctype-runtime", "locale-runtime")
            ),
            new Spec(
                "0x0056aff4",
                "CRT__AllocOsHandleSlot",
                new String[] {},
                "int CRT__AllocOsHandleSlot(void)",
                "Wave883 static read-back: CRT__OpenFd target allocates an OS-handle table slot. It locks index 0x12, scans DAT_009d32a0 table blocks in 0x20-handle chunks, initializes per-slot critical sections under lock index 0x11, allocates a 0x480-byte block with _malloc when no free block exists, bumps DAT_009d33a0, and calls CRT__LockFileHandleByIndex on the first new slot. Static evidence only; exact CRT file table layout remains unproven.",
                tags("file-descriptor-runtime", "heap-runtime", "lock-runtime")
            ),
            new Spec(
                "0x0056be17",
                "CRT__InitCTypeTablesFromCodePage",
                new String[] {},
                "int CRT__InitCTypeTablesFromCodePage(void)",
                "Wave883 static read-back: initializes CRT ctype tables from DAT_009d0998/DAT_009d09a8. It resets PTR_DAT_00653890/PTR_DAT_00653894 and frees DAT_009d0aec/DAT_009d0af0 when no codepage is active; otherwise allocates 0x202/0x202/0x101/0x202 buffers, calls GetCPInfo, CRT__GetStringTypeACompat, and CRT__GetStringTypeWideOrAnsiCompat_0056defa, marks lead-byte ranges with 0x8000, then swaps global table pointers. Static evidence only; exact ctype table schema remains unproven.",
                tags("ctype-runtime", "locale-runtime", "heap-runtime")
            ),
            new Spec(
                "0x0056c05c",
                "CRT__ReturnZero",
                new String[] {},
                "int CRT__ReturnZero(void)",
                "Wave883 static read-back: two-instruction return-zero helper referenced by CRT__HandleFpStatusAndReturnDouble and CRT__HandleFloatingPointException. Static evidence only; exact callback-table role remains unproven.",
                tags("math-exception-runtime", "small-helper-runtime")
            ),
            new Spec(
                "0x0056c2af",
                "CRT__FindLocaleForLanguageAndCountry_0056c2af",
                new String[] {},
                "void CRT__FindLocaleForLanguageAndCountry_0056c2af(void)",
                "Wave883 static read-back: CRT__ResolveLocaleNameAndMetadata_NlsCore target for language+country locale matching. It measures DAT_009d0b28 and DAT_009d0b2c with _strlen, sets 3-letter flags DAT_009d0b24/DAT_009d0b1c, computes DAT_009d0b20 via CRT__CountAlphaPrefix when needed, calls EnumSystemLocalesA(CRT__EnumLocalesCallback_MatchLanguageCountry, 1), and clears DAT_009d0b30 unless required match bits survive. Static evidence only; exact locale selection behavior remains unproven.",
                tags("locale-runtime", "nls-runtime")
            ),
            new Spec(
                "0x0056c53a",
                "CRT__FindLocaleForLanguageOnly_0056c53a",
                new String[] {},
                "void CRT__FindLocaleForLanguageOnly_0056c53a(void)",
                "Wave883 static read-back: CRT__ResolveLocaleNameAndMetadata_NlsCore target for language-only locale matching. It measures DAT_009d0b28, sets DAT_009d0b24/DAT_009d0b20, calls EnumSystemLocalesA(CRT__EnumLocalesCallback_MatchLanguageOnly, 1), and clears DAT_009d0b30 when bit 4 is absent. Static evidence only; exact locale selection behavior remains unproven.",
                tags("locale-runtime", "nls-runtime")
            ),
            new Spec(
                "0x0056c64d",
                "CRT__FindLocaleForCountryOnly_0056c64d",
                new String[] {},
                "void CRT__FindLocaleForCountryOnly_0056c64d(void)",
                "Wave883 static read-back: CRT__ResolveLocaleNameAndMetadata_NlsCore target for country-only locale matching. It measures DAT_009d0b2c, sets DAT_009d0b1c for 3-letter country tokens, calls EnumSystemLocalesA(CRT__ValidateCodePageAgainstLocale, 1), and clears DAT_009d0b30 when bit 4 is absent. Static evidence only; exact locale/codepage validation behavior remains unproven.",
                tags("locale-runtime", "nls-runtime")
            ),
            new Spec(
                "0x0056c70a",
                "CRT__InitLocaleDefaults",
                new String[] {},
                "void CRT__InitLocaleDefaults(void)",
                "Wave883 static read-back: CRT__ResolveLocaleNameAndMetadata_NlsCore target that ORs DAT_009d0b30 with 0x104, calls GetUserDefaultLCID, and stores the result into DAT_009d0b34 and DAT_009d0b18. Static evidence only; exact locale metadata schema remains unproven.",
                tags("locale-runtime", "nls-runtime")
            ),
            new Spec(
                "0x0056c80b",
                "CRT__IsWindowsNtPlatform",
                new String[] {},
                "int CRT__IsWindowsNtPlatform(void)",
                "Wave883 static read-back: CRT__ResolveLocaleNameAndMetadata_NlsCore target that fills _OSVERSIONINFOA size 0x94, calls GetVersionExA, and returns 1 only when dwPlatformId equals 2. Static evidence only; exact OS-compatibility branch role remains unproven.",
                tags("platform-runtime", "locale-runtime")
            ),
            new Spec(
                "0x0056c998",
                "CRT__StrToLongWithBaseAndLocaleCType",
                new String[] {},
                "int CRT__StrToLongWithBaseAndLocaleCType(void)",
                "Wave883 static read-back: CRT__StrToLong core plus mode1 thunk target. It skips locale whitespace with PTR_DAT_00653890 or CRT__GetCharTypeMask_Compat mask 8, handles sign and base 0/8/10/16 with 0x/0X prefix detection, converts digits/letters using CRT__ToUpperWithLocaleLock, tracks overflow against 0xffffffff/base, writes end pointer, and sets errno 0x22 through CRT__GetErrnoThreadPtr_00567aa8 on overflow. Static evidence only; exact strtol compatibility remains unproven.",
                tags("string-runtime", "locale-runtime", "errno-runtime")
            ),
            new Spec(
                "0x0056cbb4",
                "CRT__EnsureTzsetInitialized",
                new String[] {},
                "void CRT__EnsureTzsetInitialized(void)",
                "Wave883 static read-back: CRT__SystemTimeToUnixTimestampLocal target that lazily initializes timezone state. If DAT_009d0bf8 is zero, it locks index 0xb, calls CRT__Tzset once, increments DAT_009d0bf8, and unlocks index 0xb. Static evidence only; exact CRT timezone initialization contract remains unproven.",
                tags("time-runtime", "timezone-runtime", "lock-runtime")
            ),
            new Spec(
                "0x0056cbe2",
                "CRT__Tzset",
                new String[] {},
                "void CRT__Tzset(void)",
                "Wave883 static read-back: timezone setup routine. It locks index 0xc, queries TZ via CRT__GetEnvVarValuePointerCaseInsensitive, otherwise calls GetTimeZoneInformation and converts standard/daylight names through WideCharToMultiByte into PTR_DAT_00656a14/PTR_DAT_00656a18; TZ path caches DAT_009d0bf4, parses offsets with CRT__ParseDecimalIntA, writes DAT_00656988/DAT_0065698c/_DAT_00656990, and uses _strncpy/_strcmp/_strlen/_malloc/free helpers. Static evidence only; exact TZ grammar and DST runtime behavior remain unproven.",
                tags("time-runtime", "timezone-runtime", "environment-runtime")
            ),
            new Spec(
                "0x0056defa",
                "CRT__GetStringTypeWideOrAnsiCompat_0056defa",
                new String[] {},
                "int CRT__GetStringTypeWideOrAnsiCompat_0056defa(void)",
                "Wave883 static read-back: GetStringTypeW/A bridge used by CRT__GetCharTypeMaskCompat and CRT__InitCTypeTablesFromCodePage. It probes GetStringTypeW versus GetStringTypeA into DAT_009d0c2c, directly calls GetStringTypeW on the W path, or converts wide input through WideCharToMultiByte with flags 0x220 before GetStringTypeA and CRT__MemMoveOverlapSafe. Static evidence only; exact NLS fallback behavior remains unproven.",
                tags("nls-runtime", "ctype-runtime", "locale-runtime")
            )
        };

        Stats stats = new Stats();
        println("Wave883 CRT locale/string/runtime tail mode=" + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave883 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }
}
