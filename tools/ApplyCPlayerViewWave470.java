//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCPlayerViewWave470 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String oldName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.oldName = oldName;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cplayer-view-wave470",
            "retail-binary-evidence",
            "source-bridge"
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.oldName) && !fn.getName().equals(spec.name)) {
                throw new IllegalStateException(
                    "Unexpected function name at " + spec.address + ": " + fn.getName()
                );
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                if (needsRename) {
                    stats.wouldRename++;
                }
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            String expectedSignature = expectedSignature(spec);
            if (!actualSignature.equals(expectedSignature)) {
                throw new IllegalStateException(
                    "Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature
                );
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d2780",
                "CPlayer__ctor_like_004d2780",
                "CPlayer__ctor",
                "__thiscall",
                voidPtr,
                "Wave470 name/signature/comment correction: source-adjacent CPlayer constructor. Retail body installs the CPlayer vtable at 0x005de770, clears controller/monitor fields, nulls the active BattleEngine reader, zeroes stats, stores the player number argument at +0x2c, seeds current/preferred view modes to first-person, clears kill counters, and reads a CAREER-adjacent per-player flag into +0x20. Source bridge: Player.cpp CPlayer::CPlayer(int number). Static retail/source evidence only; concrete CPlayer layout, exact CAREER field naming/indexing, runtime player setup, and rebuild parity remain unproven.",
                tags("cplayer", "constructor", "camera-view", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("player_number", intType)
                }
            ),
            new Spec(
                "0x004d2810",
                "CPlayer__VFunc_01_004d2810",
                "CPlayer__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave470 name/signature/comment correction: scalar-deleting destructor wrapper for the CPlayer vtable at 0x005de770. It calls CPlayer__dtor_base, tests flags bit 0 from the ret 0x4 stack argument, optionally frees this through CDXMemoryManager, and returns this. Static retail/vtable evidence only; runtime player lifetime behavior and rebuild parity remain unproven.",
                tags("cplayer", "destructor", "scalar-deleting-dtor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004d2830",
                "CPlayer__ctor_like_004d2830",
                "CPlayer__dtor_base",
                "__fastcall",
                voidType,
                "Wave470 name/signature/comment correction: CPlayer destructor-base cleanup. Retail body restores the CPlayer vtable, removes the active BattleEngine reader cell at +0x1c from its owner set when linked, and delegates to CMonitor__Shutdown. Source bridge: empty CPlayer::~CPlayer body plus inherited monitor/active-reader cleanup in retail. Static retail/source evidence only; exact field ownership, runtime lifetime behavior, and rebuild parity remain unproven.",
                tags("cplayer", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004d28a0",
                "CPlayer__Init",
                "CPlayer__Init",
                "__fastcall",
                voidType,
                "Wave470 signature/comment hardening: CPlayer::Init source match. Retail body calls CPlayer__GotoFPView, then stores PLATFORM__GetSysTimeFloat() into +0x4c as the timeout timestamp. Static retail/source evidence only; exact CPlayer layout, runtime camera selection, and rebuild parity remain unproven.",
                tags("cplayer", "camera-view", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004d28c0",
                "CPlayer__GotoFPView",
                "CPlayer__GotoFPView",
                "__fastcall",
                voidType,
                "Wave470 signature/comment hardening: CPlayer::GotoFPView source match. Retail body returns when the BattleEngine active-reader pointer at +0x1c is null, stores current view mode 1 at +0x24, allocates an 8-byte CThingCamera-style camera object, links it to the BattleEngine reader, and calls CGame__SetCurrentCamera with player_number-1. Static retail/source evidence only; exact camera object layout, runtime camera behavior, and rebuild parity remain unproven.",
                tags("cplayer", "camera-view", "first-person-view", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004d29c0",
                "CPlayer__Goto3rdPersonView",
                "CPlayer__Goto3rdPersonView",
                "__fastcall",
                voidType,
                "Wave470 signature/comment hardening: CPlayer::Goto3rdPersonView source match. Retail body returns when the BattleEngine active-reader pointer at +0x1c is null, stores current view mode 2 at +0x24, allocates a 0xc-byte third-person camera object, calls CThing3rdPersonCamera__ctor with the BattleEngine reader, and calls CGame__SetCurrentCamera with player_number-1. Static retail/source evidence only; exact camera object layout, runtime camera behavior, and rebuild parity remain unproven.",
                tags("cplayer", "camera-view", "third-person-view", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004d2a50",
                "CPlayer__GotoControlView",
                "CPlayer__GotoControlView",
                "__fastcall",
                voidType,
                "Wave470 signature/comment hardening: CPlayer::GotoControlView source match. Retail body reads preferred control view mode at +0x28, dispatches to CPlayer__GotoFPView for mode 1, and dispatches to CPlayer__Goto3rdPersonView for mode 2. Static retail/source evidence only; exact enum names, runtime camera behavior, and rebuild parity remain unproven.",
                tags("cplayer", "camera-view", "control-view", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.bad != 0 || stats.missing != 0) {
            throw new RuntimeException("Wave470 CPlayer view apply failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
