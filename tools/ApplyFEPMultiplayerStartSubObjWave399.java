//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyFEPMultiplayerStartSubObjWave399 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
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
            "fepmultiplayerstart-subobj-wave399",
            "frontend",
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                throw new IllegalStateException("Function not found at " + spec.address);
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
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
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00459810",
                "CFEPMultiplayerStart__SubObj39B8__QueuePageId",
                "__thiscall",
                voidType,
                "Wave399 comment hardening: SubObj39B8 helper queues the requested multiplayer-start page id by setting +0xc active/dirty state and copying page_id into +0x10 and +0x8. Static retail evidence only; exact source identity, concrete helper layout, runtime multiplayer behavior, and rebuild parity remain unproven.",
                tags("queue-helper", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("page_id", intType)
                }
            ),
            new Spec(
                "0x00459920",
                "CFEPMultiplayerStart__SubObj8848__ctor",
                "__thiscall",
                voidPtr,
                "Wave399 signature/comment correction: SubObj8848 constructor installs vtable 0x005db4fc, zeros the compact per-row selection table, seeds default level-code constants, sets the row count at +0x345c, and clears the 300-entry selection/highlight grid. Static retail evidence only; exact source identity, concrete helper layout, runtime multiplayer behavior, and rebuild parity remain unproven.",
                tags("constructor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004599a0",
                "CFEPMultiplayerStart__SubObj8848__Init",
                "__thiscall",
                intType,
                "Wave399 signature/comment correction: vtable slot 0 initializer scans the seeded 6-column level grid for DAT_0089d94c, records the current selection row/column at +0x3468/+0x346c, computes the scroll target/offset, and refreshes two animation timestamps. Static retail evidence only; exact source identity, concrete helper layout, runtime multiplayer behavior, and rebuild parity remain unproven.",
                tags("vtable-slot-0", "init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00459a60",
                "CFEPMultiplayerStart__SubObj8848__ActiveNotification",
                "__thiscall",
                voidType,
                "Wave399 comment hardening: active-notification hook resets the inactivity timer and, when entered from frontend pages 5/6, immediately raises the current row/column selection highlight in the +0x57c grid. Static retail evidence only; exact source identity, concrete helper layout, runtime multiplayer behavior, and rebuild parity remain unproven.",
                tags("active-notification", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_page", intType)
                }
            ),
            new Spec(
                "0x00459aa0",
                "CFEPMultiplayerStart__SubObj8848__TransitionNotification",
                "__thiscall",
                voidType,
                "Wave399 comment hardening: transition-notification hook records the transition timestamp, clears the 300-entry selection/highlight grid, and restores the current highlight when transitioning from pages 5/6. Static retail evidence only; exact source identity, concrete helper layout, runtime multiplayer behavior, and rebuild parity remain unproven.",
                tags("transition-notification", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_page", intType)
                }
            ),
            new Spec(
                "0x00459b00",
                "CFEPMultiplayerStart__SubObj8848__Process",
                "__thiscall",
                voidType,
                "Wave399 comment hardening: process hook eases the scroll offset toward the selected row, fades the 50x6 selection/highlight grid toward the active cell when menu_state is 0, increments the inactivity counter, and falls back to page 0x0c after the timeout threshold. Static retail evidence only; exact source identity, concrete helper layout, runtime multiplayer behavior, and rebuild parity remain unproven.",
                tags("process-hook", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("menu_state", intType)
                }
            ),
            new Spec(
                "0x00459c10",
                "CFEPMultiplayerStart__SubObj8848__ButtonPressed",
                "__thiscall",
                voidType,
                "Wave399 comment hardening: button handler processes horizontal/vertical navigation, select/back page transitions, sound feedback, DAT_0089d94c selected-level update, row/column clamping, scroll target recalculation, and level/episode animation timestamp refreshes. Static retail evidence only; exact source identity, concrete helper layout, runtime multiplayer behavior, and rebuild parity remain unproven.",
                tags("button-handler", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("button", intType)
                }
            ),
            new Spec(
                "0x00459e50",
                "CFEPMultiplayerStart__SubObj8848__RenderPreCommon",
                "__stdcall",
                voidType,
                "Wave399 signature/comment correction: render-pre-common vtable slot uses RET 0x8 and consumes transition/dest stack arguments with no saved this use; it gates on transition, computes a clamped fade alpha, and draws the scaled video quad backdrop. Static retail evidence only; exact source identity, concrete helper layout, runtime multiplayer behavior, and rebuild parity remain unproven.",
                tags("render-precommon", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("transition", floatType),
                    param("dest", intType)
                }
            ),
            new Spec(
                "0x00459ee0",
                "CFEPMultiplayerStart__SubObj8848__Render",
                "__thiscall",
                voidType,
                "Wave399 comment hardening: render hook draws the multiplayer-start selection grid and cell effects, clamps transition alpha, resolves selected level and episode text, renders the E3 2002 build/progress string, help prompts, overlay effects, and title bar. Static retail evidence only; exact source identity, concrete helper layout, runtime multiplayer behavior, and rebuild parity remain unproven.",
                tags("render-hook", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("transition", floatType),
                    param("dest", intType)
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
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave399 FEPMultiplayerStart SubObj apply had failures");
        }
    }
}
