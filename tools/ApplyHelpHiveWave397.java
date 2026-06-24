//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyHelpHiveWave397 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.createIfMissing = createIfMissing;
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
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

    private String[] tags(String owner, String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "help-hive-wave397",
            owner,
            "retail-binary-evidence"
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

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }
        if (dryRun) {
            println("DRY: would create " + spec.address + " " + spec.name);
            stats.wouldCreate++;
            return null;
        }

        Address address = addr(spec.address);
        disassemble(address);
        fn = createFunction(address, null);
        if (fn == null) {
            fn = functionAtEntry(spec.address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        fn.setName(spec.name, SourceType.USER_DEFINED);
        stats.created++;
        println("OK: created " + spec.address + " " + spec.name);
        return fn;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getOrCreate(spec, dryRun, stats);
            if (fn == null) {
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (IllegalStateException ex) {
            if (ex.getMessage() != null && ex.getMessage().startsWith("Function not found")) {
                stats.missing++;
            } else {
                stats.bad++;
            }
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
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
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0047fab0",
                "CHelpTextDisplay__ctor",
                "__thiscall",
                voidPtr,
                "Wave397 owner/signature/comment correction: CHelpTextDisplay constructor zeroes the two queued-message slots, installs the HelpTextDisplay vtable, returns this, and is allocated by CGame during restart/init setup. Static retail evidence only; exact source identity, concrete HelpTextDisplay layout, runtime HelpText behavior, and rebuild parity remain unproven.",
                new String[] {"CHelpTextDisplay__ctor_like_0047fab0"},
                tags("helptext", "constructor", "name-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047fad0",
                "CHelpTextDisplay__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave397 boundary/signature/comment recovery: scalar deleting destructor restores the HelpTextDisplay vtable and frees this through the OID allocator when flags bit 1 is set. Static retail evidence only; exact source identity, concrete HelpTextDisplay layout, runtime HelpText behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("helptext", "destructor", "function-boundary", "signature-corrected", "comment-hardened"),
                true,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x0047fb00",
                "CHelpTextDisplay__QueueMessageWithTimestamp",
                "__thiscall",
                voidType,
                "Wave397 owner/signature/comment correction: corrects the older CUnitAI owner label to HelpTextDisplay. The helper queues a message pointer into one of two queued-message slots, stamps it with the global timestamp, marks the slot active, and logs the too many messages error if both slots are occupied. Static retail evidence only; exact source identity, concrete HelpTextDisplay layout, runtime HelpText behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__QueueMessageWithTimestamp"},
                tags("helptext", "message-queue", "owner-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("message", voidPtr)
                }
            ),
            new Spec(
                "0x0047fb50",
                "CHelpTextDisplay__RenderQueuedMessages",
                "__fastcall",
                voidType,
                "Wave397 owner/signature/comment correction: corrects the older CExplosionInitThing owner label to HelpTextDisplay. The body renders up to two queued HelpText messages, uses age/fade timing, wraps text through TextLayout__WrapWideTextToFixedLines, optionally toggles controller-config font state, and expires old slots. Static retail evidence only; exact source identity, concrete HelpTextDisplay layout, runtime HelpText behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__RenderOverlayMarkerTextWithDistanceFade"},
                tags("helptext", "rendering", "owner-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047fe30",
                "CHiveBoss__Init",
                "__thiscall",
                voidType,
                "Wave397 signature/comment correction: corrects the undefined saved signature to thiscall with init_data. The initializer sets HiveBoss init-data flags, allocates the destructable-segment controller, constructs the HiveBoss mesh controller, calls CUnit__Init, resolves the core2 segment, creates a guide object, and seeds HiveBoss floats. Static retail evidence only; exact source identity, concrete CHiveBoss layout, runtime HiveBoss behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("hiveboss", "init", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_data", voidPtr)
                }
            ),
            new Spec(
                "0x004804c0",
                "CHiveBoss__SetVar",
                "__thiscall",
                voidType,
                "Wave397 owner/signature/comment correction: corrects the older CExplosionInitThing owner label to HiveBoss SetVar context. The helper matches hb_* config names, writes config float fields including guide velocities, rotation speeds, safe distance, and minimum ground clearance, then falls back to the base SetVar unknown-var path. Static retail evidence only; exact source identity, concrete CHiveBoss layout, runtime HiveBoss behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__ApplyHBConfigField"},
                tags("hiveboss", "setvar", "owner-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("name", voidPtr),
                    param("data", voidPtr)
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

        if (!dryRun && (stats.missing != 0 || stats.bad != 0)) {
            throw new IllegalStateException("Wave397 HelpText/HiveBoss apply had failures");
        }
    }
}
