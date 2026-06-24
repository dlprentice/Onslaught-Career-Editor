//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyDisplayMediaThreadWave571 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
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

    private Function getFunctionOrReport(Spec spec, Stats stats) {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "display-media-thread-wave571",
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
            Function fn = getFunctionOrReport(spec, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
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

            Function readBack = functionAtEntry(addr(spec.address));
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

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
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
        DataType boolType = BooleanDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005286e0",
                "CD3DApplication__LoadCardIdAndApplyVendorTweaks",
                "__cdecl",
                voidType,
                "Wave571 signature/comment hardening: retail-only cardid.txt tweak loader. The sole caller is CD3DApplication__Initialize3DEnvironment at 0x0052af3f; the helper opens the supplied path, parses CardID Version/Vendor/Device/range/tweak lines against the current adapter identifier table at DAT_00855bdc-family, scans the global CVar list at DAT_0089c018, logs Setting tweak text, and invokes the matching CVar vfunc. Static retail evidence only; exact source identity, exact cardid grammar, runtime D3D behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__LoadCardIdAndApplyVendorTweaks"},
                tags("display", "cardid", "tweak-loader", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("cardid_path", voidPtr)
                }
            ),
            new Spec(
                "0x00528aa0",
                "CVar__Init",
                "__thiscall",
                voidType,
                "Wave571 signature hardening: CVar constructor/init helper. RET 0x8 confirms two stack arguments after this; the body installs the base/vfunc table, stores cvar_name at this+0x08, links this into global list DAT_0089c018 through this+0x04, installs the CVar__SetValueRounded vfunc table, and stores initial_value at this+0x0c. Static retail evidence only; exact source identity, concrete CVar layout, runtime console behavior, and rebuild parity remain unproven.",
                new String[] {"CVar__Init"},
                tags("cvar", "constructor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("cvar_name", voidPtr),
                    param("initial_value", intType)
                }
            ),
            new Spec(
                "0x00528ad0",
                "CVar__SetValueRounded",
                "__thiscall",
                voidType,
                "Wave571 signature hardening: CVar numeric setter. RET 0x4 confirms one stack float after this; the body rounds value with FISTP and stores the integer result into this+0x0c. Xrefs include options loading, CLTShell initialization, landscape render settings, front-end video init, and mesh quality setup. Static retail evidence only; exact source identity, concrete CVar layout, runtime option behavior, and rebuild parity remain unproven.",
                new String[] {"CVar__SetValueRounded"},
                tags("cvar", "numeric-setter", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("value", floatType)
                }
            ),
            new Spec(
                "0x00528af0",
                "CDXTexture__IsResourceHandleValid",
                "__thiscall",
                boolType,
                "Wave571 signature/comment hardening: ECX-only texture/resource-handle predicate. The body reads this+0x0c, compares it with -1, returns whether the handle is valid, and is called repeatedly from CDXTexture__LoadTextureFromFile plus CVBufTexture__SetupSecondaryBlend. Static retail evidence only; exact CDXTexture layout, runtime texture loading behavior, source identity, and rebuild parity remain unproven.",
                new String[] {"CDXTexture__IsResourceHandleValid"},
                tags("texture", "resource-handle", "predicate", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00528b00",
                "CEngine__InvokeCallbackIfStateMinusOne",
                "__thiscall",
                voidType,
                "Wave571 signature hardening: one-argument callback gate. RET 0x4 confirms the old second stack parameter was phantom; when this+0x0c equals -1, the helper converts callback_value to float and calls the first vfunc through this. No owner rename was made because xrefs are mostly raw/no-function static initializers. Static retail evidence only; exact owner/source identity, callback contract, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CEngine__InvokeCallbackIfStateMinusOne"},
                tags("callback-gate", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("callback_value", intType)
                }
            ),
            new Spec(
                "0x00528b60",
                "CBinkOpenThread__WorkerMain",
                "__stdcall",
                intType,
                "Wave571 signature/comment hardening: Win32 thread proc for waiting-thread/Bink-style async work. RET 0x4 confirms one thread_obj pointer argument; the loop waits on event at +0x0c, exits when shutdown flag +0x14 is set, waits on mutex +0x08, invokes the object vfunc, clears running flag +0x15, releases the mutex, signals completion event +0x10, and returns 0. Static retail evidence only; exact class layout, runtime Bink/media behavior, source identity, and rebuild parity remain unproven.",
                new String[] {"CBinkOpenThread__WorkerMain"},
                tags("bink-thread", "thread-proc", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("thread_obj", voidPtr)
                }
            ),
            new Spec(
                "0x00528bc0",
                "CWaitingThread__ctor_base",
                "__thiscall",
                voidPtr,
                "Wave571 owner/name/signature hardening: base waiting-thread constructor. ECX-only body leaves EAX as this, initializes handle slots +0x04/+0x08/+0x0c/+0x10 to -1, installs the waiting-thread vtable, clears shutdown/running flags +0x14/+0x15, and links this into global waiting-thread list DAT_0089c01c at +0x18. Xrefs from COggLoader, CBinkOpenThread, and CMissionScriptObjectCode constructors support the base waiting-thread name. Static retail evidence only; exact class layout, destructor behavior, runtime threading behavior, and rebuild parity remain unproven.",
                new String[] {"CWaitingThread__ctor_like_00528bc0", "CWaitingThread__ctor_base"},
                tags("waiting-thread", "constructor", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00528c70",
                "CBinkOpenThread__Init",
                "__thiscall",
                boolType,
                "Wave571 signature/comment hardening: ECX-only waiting-thread initialization helper. It lazily creates the mutex at +0x08, work event at +0x0c, completion event at +0x10, and worker thread at +0x04 using CBinkOpenThread__WorkerMain, then returns true only when all handles are neither -1 nor null. Static retail evidence only; exact class layout, runtime thread scheduling, source identity, and rebuild parity remain unproven.",
                new String[] {"CBinkOpenThread__Init"},
                tags("bink-thread", "thread-init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00528d10",
                "CBinkOpenThread__WaitForThread",
                "__thiscall",
                voidType,
                "Wave571 signature/comment hardening: ECX-only wait helper. After CBinkOpenThread__Init succeeds, it spins with Sleep(0) while running flag +0x15 is set, then waits on mutex +0x08 before returning. Xrefs include mission object-code async load, front-end video open, and message-box voice/text reveal. Static retail evidence only; exact class layout, runtime media behavior, source identity, and rebuild parity remain unproven.",
                new String[] {"CBinkOpenThread__WaitForThread"},
                tags("bink-thread", "wait-helper", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00528d50",
                "CBinkOpenThread__StartAsync",
                "__thiscall",
                voidType,
                "Wave571 signature/comment hardening: ECX-only async-start helper. It sets running flag +0x15, releases mutex +0x08, and signals work event +0x0c. Xrefs include mission object-code async load, front-end video open, and message-box voice/text reveal. Static retail evidence only; exact class layout, runtime media behavior, source identity, and rebuild parity remain unproven.",
                new String[] {"CBinkOpenThread__StartAsync"},
                tags("bink-thread", "async-start", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00528d70",
                "CBinkOpenThread__RunSync",
                "__thiscall",
                voidType,
                "Wave571 signature/comment hardening: ECX-only synchronous-run helper. It invokes the object's first vfunc immediately and then releases mutex +0x08. CDXFrontEndVideo__Open is the named caller in the current xref export. Static retail evidence only; exact class layout, runtime media behavior, source identity, and rebuild parity remain unproven.",
                new String[] {"CBinkOpenThread__RunSync"},
                tags("bink-thread", "sync-run", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00528d90",
                "CBinkOpenThread__IsRunning",
                "__thiscall",
                boolType,
                "Wave571 signature/comment hardening: ECX-only running-flag reader. The body returns the signed byte at this+0x15; xrefs include Bink voice queue pumping, front-end video open/close/render, and Goodies loading polling. Static retail evidence only; exact class layout, runtime media behavior, source identity, and rebuild parity remain unproven.",
                new String[] {"CBinkOpenThread__IsRunning"},
                tags("bink-thread", "field-reader", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00528da0",
                "CBinkOpenThread__Lock",
                "__thiscall",
                voidType,
                "Wave571 signature/comment hardening: ECX-only lock helper. It ensures CBinkOpenThread__Init has run, then waits indefinitely on mutex +0x08. Xrefs include Bink voice queue pumping, CDXFrontEndVideo update/init/close/render, and Goodies loading polling. Static retail evidence only; exact class layout, runtime media behavior, source identity, and rebuild parity remain unproven.",
                new String[] {"CBinkOpenThread__Lock"},
                tags("bink-thread", "lock-helper", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00528dc0",
                "CBinkOpenThread__Unlock",
                "__thiscall",
                voidType,
                "Wave571 signature/comment hardening: ECX-only unlock helper. The body releases mutex +0x08; xrefs include Bink voice queue pumping, CDXFrontEndVideo update/init/close/render, and Goodies loading polling. Static retail evidence only; exact class layout, runtime media behavior, source identity, and rebuild parity remain unproven.",
                new String[] {"CBinkOpenThread__Unlock"},
                tags("bink-thread", "unlock-helper", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave571 display/media/thread tranche failed");
        }
    }
}
