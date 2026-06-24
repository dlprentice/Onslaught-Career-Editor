//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyParticleEffectLinkWave477 extends GhidraScript {
    private static final String ADDRESS = "0x004cb0b0";
    private static final String OLD_NAME = "CUnit__FinalizeLinkedUnitStateAndClear";
    private static final String NEW_NAME = "ParticleEffectLink__SetHandleStateAndClear";
    private static final String CALLING_CONVENTION = "__thiscall";
    private static final String COMMENT =
        "Wave477 owner/signature correction: RET 0x4 and caller push evidence prove one stack argument, not the prior extra param_2. This helper operates on a small particle/effect owner-link cell rather than a whole CUnit object: it reads the linked effect handle at this +0x4, writes handle +0xb4 to 1 when set_state_one is 1 or to 2 otherwise, then clears this +0x4. Xrefs come from CUnit, BattleEngine, Mine, particle descriptor, RTMesh, trigger, projectile, and raw non-function cleanup contexts, so the old CUnit owner is too narrow. Static retail-binary evidence only; exact owner-link/handle layouts, raw caller boundaries, runtime particle/effect behavior, exact source identity, and rebuild parity remain unproven.";
    private static final String[] TAGS = {
        "static-reaudit",
        "particle-effect-link-wave477",
        "retail-binary-evidence",
        "particle",
        "effect-handle",
        "owner-corrected",
        "signature-corrected",
        "comment-hardened"
    };

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

    private String expectedSignature(ParameterImpl[] parameters) {
        StringBuilder sb = new StringBuilder();
        sb.append("void ").append(CALLING_CONVENTION).append(" ").append(NEW_NAME).append("(");
        for (int i = 0; i < parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(parameters[i].getDataType().getDisplayName()).append(" ").append(parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        ParameterImpl[] parameters = new ParameterImpl[] {
            param("this", voidPtr),
            param("set_state_one", intType)
        };
        String expectedSignature = expectedSignature(parameters);

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;

        try {
            Function fn = functionAtEntry(ADDRESS);
            if (fn == null) {
                missing++;
                println("FAIL: " + ADDRESS + " Function not found");
            } else {
                boolean nameNeedsChange = !fn.getName().equals(NEW_NAME);
                if (!fn.getName().equals(OLD_NAME) && nameNeedsChange) {
                    throw new IllegalStateException("Unexpected function name: " + fn.getName());
                }

                if (dryRun) {
                    println("DRY: " + ADDRESS + " " + fn.getName() + " -> " + expectedSignature);
                    skipped++;
                    if (nameNeedsChange) {
                        wouldRename++;
                    }
                } else {
                    if (nameNeedsChange) {
                        fn.setName(NEW_NAME, SourceType.USER_DEFINED);
                        renamed++;
                    }
                    fn.setCallingConvention(CALLING_CONVENTION);
                    fn.setReturnType(voidType, SourceType.USER_DEFINED);
                    fn.replaceParameters(
                        FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                        true,
                        SourceType.USER_DEFINED,
                        parameters
                    );
                    fn.setComment(COMMENT);
                    for (String tag : TAGS) {
                        fn.addTag(tag);
                    }

                    Function readBack = functionAtEntry(ADDRESS);
                    if (readBack == null) {
                        throw new IllegalStateException("Read-back missing");
                    }
                    if (!readBack.getName().equals(NEW_NAME)) {
                        throw new IllegalStateException("Read-back name mismatch: " + readBack.getName());
                    }
                    String actualSignature = readBack.getSignature().toString();
                    if (!actualSignature.equals(expectedSignature)) {
                        throw new IllegalStateException("Read-back signature mismatch: " + actualSignature + " != " + expectedSignature);
                    }
                    if (!COMMENT.equals(readBack.getComment())) {
                        throw new IllegalStateException("Read-back comment mismatch");
                    }
                    Set<String> actualTags = tagNames(readBack);
                    for (String tag : TAGS) {
                        if (!actualTags.contains(tag)) {
                            throw new IllegalStateException("Read-back missing tag: " + tag);
                        }
                    }

                    updated++;
                    println("OK: " + ADDRESS + " " + readBack.getName() + " -> " + actualSignature);
                }
            }
        } catch (Exception ex) {
            bad++;
            println("FAIL: " + ADDRESS + " " + ex.getMessage());
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + updated +
            " skipped=" + skipped +
            " created=0 would_create=0" +
            " renamed=" + renamed +
            " would_rename=" + wouldRename +
            " missing=" + missing +
            " bad=" + bad
        );

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave477 apply had missing/bad targets");
        }
    }
}
