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

public class ApplyCFEPDebriefingBoundaryRecoveryWave981 extends GhidraScript {
    private static class ParamSpec {
        final String name;
        final DataType type;

        ParamSpec(String name, DataType type) {
            this.name = name;
            this.type = type;
        }
    }

    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final ParamSpec[] params;

        Spec(String address, String name, String callingConvention, DataType returnType, String comment, ParamSpec... params) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.params = params;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(ParamSpec spec) throws Exception {
        return new ParameterImpl(spec.name, spec.type, currentProgram);
    }

    private ParameterImpl[] params(Spec spec) throws Exception {
        ParameterImpl[] result = new ParameterImpl[spec.params.length];
        for (int i = 0; i < spec.params.length; i++) {
            result[i] = param(spec.params[i]);
        }
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].type.getDisplayName()).append(" ").append(spec.params[i].name);
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(expectedSignature(spec));
    }

    private void applySignature(Function fn, Spec spec) throws Exception {
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, params(spec));
    }

    private boolean hasAllTags(Function fn, String[] expectedTags) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expectedTags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private static DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private static ParamSpec p(String name, DataType type) {
        return new ParamSpec(name, type);
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x00456930",
                "CFEPDebriefing__Process",
                "__thiscall",
                VoidDataType.dataType,
                "Wave981 CFEPDebriefing boundary recovery: recovered the missing Ghidra function object for vtable slot 2 at 0x005db9c8. Static evidence: long process body updates debriefing timers and entry-state fields, dispatches button 0x2c through the page vtable when appropriate, updates debriefing node/particle positions, and reaches first observed terminal 0x00456d32 RET 0x4. Static retail Ghidra evidence only; exact CFEPDebriefing source-body identity, concrete debriefing-page layout, runtime frontend/debrief behavior, BEA patching, and rebuild parity remain separate proof.",
                p("this", voidPtr()),
                p("state", IntegerDataType.dataType)
            ),
            new Spec(
                "0x004568a0",
                "CFEPDebriefing__ButtonPressed",
                "__thiscall",
                VoidDataType.dataType,
                "Wave981 CFEPDebriefing boundary recovery: recovered the missing Ghidra function object for vtable slot 3 at 0x005db9cc. Static evidence: button handler consumes button and value stack arguments, handles button 0x2c/0x2d/0x2e branches, can route frontend pages through CFrontEnd__SetPage, plays frontend sound feedback, and reaches first observed terminal 0x00456928 RET 0x8. Static retail Ghidra evidence only; exact button semantics, source-body identity, concrete debriefing-page layout, runtime frontend input behavior, BEA patching, and rebuild parity remain separate proof.",
                p("this", voidPtr()),
                p("button", IntegerDataType.dataType),
                p("value", FloatDataType.dataType)
            ),
            new Spec(
                "0x00456d40",
                "CFEPDebriefing__RenderPreCommon",
                "__stdcall",
                VoidDataType.dataType,
                "Wave981 CFEPDebriefing boundary recovery: recovered the missing Ghidra function object for vtable slot 4 at 0x005db9d0. Static evidence: stack-only render-pre-common body initializes shared frontend render globals, calls CFrontEnd__UpdateCamera, dispatches CFrontEnd__RenderVideoQuadScaledToWindow, and reaches first observed terminal 0x00456dc6 RET 0x8. Static retail Ghidra evidence only; exact source-body identity, transition/destination semantics, runtime frontend rendering, BEA patching, and rebuild parity remain separate proof.",
                p("transition", FloatDataType.dataType),
                p("dest", IntegerDataType.dataType)
            ),
            new Spec(
                "0x00456dd0",
                "CFEPDebriefing__Render",
                "__thiscall",
                VoidDataType.dataType,
                "Wave981 CFEPDebriefing boundary recovery: recovered the missing Ghidra function object for vtable slot 5 at 0x005db9d4. Static evidence: render body uses transition/dest stack arguments, calls shared frontend bracket/help/text helpers, resolves level and frontend text, renders debriefing rank/goodie/stat text through CDXFont helpers, and reaches first observed terminal 0x00457ceb RET 0x8. Static retail Ghidra evidence only; exact CFEPDebriefing source-body identity, concrete debriefing-page layout, runtime debrief text/render behavior, BEA patching, and rebuild parity remain separate proof.",
                p("this", voidPtr()),
                p("transition", FloatDataType.dataType),
                p("dest", IntegerDataType.dataType)
            ),
            new Spec(
                "0x00457cf0",
                "CFEPDebriefing__TransitionNotification",
                "__fastcall",
                VoidDataType.dataType,
                "Wave981 CFEPDebriefing boundary recovery: recovered the missing Ghidra function object for vtable slot 6 at 0x005db9d8. Static evidence: transition-notification body queries CAREER through CCareer__GetAndResetGoodieNewCount and CCareer__GetAndResetFirstGoodie, clamps debriefing state fields, clears or seeds timer/countdown fields, consumes one from_page stack argument, and reaches first observed terminal 0x00457dc3 RET 0x4. Static retail Ghidra evidence only; exact CFEPDebriefing source-body identity, concrete debriefing-page/career bridge layout, runtime debrief/goodie behavior, BEA patching, and rebuild parity remain separate proof.",
                p("this", voidPtr()),
                p("from_page", IntegerDataType.dataType)
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();
        String[] tags = new String[] {
            "static-reaudit",
            "cfepdebriefing-boundary-recovery-wave981",
            "wave981-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "frontend",
            "debriefing",
            "vtable-target",
            "comment-hardened",
            "signature-hardened"
        };

        for (Spec spec : specs()) {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            if (fn == null) {
                if (dryRun) {
                    println("WOULD_CREATE: " + spec.address + " " + spec.name);
                    stats.wouldCreate++;
                    continue;
                }
                boolean disassembled = disassemble(address);
                fn = createFunction(address, spec.name);
                if (fn == null) {
                    println("BAD: could not create function at " + spec.address + " disassembled=" + disassembled);
                    stats.bad++;
                    continue;
                }
                stats.created++;
            }

            boolean changed = false;
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    stats.wouldRename++;
                    changed = true;
                } else {
                    fn.setName(spec.name, SourceType.USER_DEFINED);
                    stats.renamed++;
                    changed = true;
                }
            }

            if (!signatureMatches(fn, spec)) {
                if (dryRun) {
                    println("WOULD_SIGNATURE: " + spec.address + " " + expectedSignature(spec));
                    stats.signatureUpdated++;
                    changed = true;
                } else {
                    applySignature(fn, spec);
                    stats.signatureUpdated++;
                    changed = true;
                }
            }

            if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
                if (dryRun) {
                    println("WOULD_COMMENT: " + spec.address);
                    stats.commentOnlyUpdated++;
                    changed = true;
                } else {
                    fn.setComment(spec.comment);
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (!hasAllTags(fn, tags)) {
                if (dryRun) {
                    println("WOULD_TAGS: " + spec.address);
                    stats.commentOnlyUpdated++;
                    changed = true;
                } else {
                    for (String tag : tags) {
                        fn.addTag(tag);
                    }
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (changed) {
                stats.updated++;
            } else {
                stats.skipped++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=0" +
            " bad=" + stats.bad
        );

        if (stats.bad != 0) {
            throw new IllegalStateException("Wave981 CFEPDebriefing boundary recovery encountered bad rows");
        }
    }
}
