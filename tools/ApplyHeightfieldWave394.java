//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyHeightfieldWave394 extends GhidraScript {
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

    private Function functionAtEntry(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Function fn = getFunctionAt(toAddr(addressText));
        if (fn == null) {
            fn = getFunctionContaining(toAddr(addressText));
            if (fn != null && !fn.getEntryPoint().equals(toAddr(addressText))) {
                fn = null;
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: missing function at " + spec.address + " for " + spec.name);
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
            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "heightfield-wave394",
            "terrain-heightfield",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0047e8e0",
                "CHeightField__InitColorGradient",
                "__fastcall",
                voidType,
                "Wave394 signature/comment hardening: ECX-backed heightfield helper derives size/mask fields from +0x1038/+0x103c, builds the 64-entry color-gradient table rooted at +0x10d0 from color fields +0x107c/+0x108c, then copies fog color triplets from +0x13c4 to +0x13d0. Static retail evidence only; source file is absent from the current Stuart snapshot, and concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("heightfield", "color-gradient", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047ea20",
                "CWorld__GetHeightSamplePacked16",
                "__fastcall",
                uintType,
                "Wave394 signature/comment hardening: samples packed 16-bit height data through the buffer pointer at +0x1028, using EDX and the stack argument as packed X/Z grid coordinates with edge wrapping/clamp branches around 0x200 and 0xa1ffe. The CWorld owner label is preserved from earlier caller-ownership evidence, but the body is heightfield-buffer evidence; exact owner/layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("heightfield", "packed-height-sample", "owner-provisional", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("heightfield_or_world", voidPtr),
                    param("x_packed", uintType),
                    param("z_packed", uintType)
                }
            ),
            new Spec(
                "0x0047eb00",
                "CHeightField__SampleInterpolatedHeight",
                "__fastcall",
                intType,
                "Wave394 signature/comment hardening: bilinearly interpolates four signed 16-bit samples from the +0x1028 height buffer using packed X/Z fixed-point coordinates and the 9x9 tile stride. Static retail evidence only; exact source identity, concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("heightfield", "bilinear-height-sample", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x_packed", uintType),
                    param("z_packed", uintType)
                }
            ),
            new Spec(
                "0x0047eb80",
                "CStaticShadows__SampleShadowHeightBilinear",
                "__fastcall",
                doubleType,
                "Wave394 signature/comment hardening: corrected the calling convention from the older saved __thiscall form to __fastcall because the read-back body consumes the world-position pointer from EDX. The helper offsets world X/Z by the global terrain origin constants, samples/interpolates signed 16-bit height data from +0x1028, scales by +0x102c, and falls back to the global zero/flat value when outside the packed terrain range. Static retail evidence only; exact source identity, concrete layout, runtime shadow/terrain behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("static-shadows", "heightfield", "bilinear-height-sample", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("world_pos", voidPtr)
                }
            ),
            new Spec(
                "0x0047ec60",
                "CMonitor__SampleHeightfieldNormalAtXY",
                "__fastcall",
                floatPtr,
                "Wave394 signature/comment hardening: writes an output normal vector from rounded world X/Z samples, returns the supplied out_normal pointer, uses the +0x1028 height buffer and +0x102c scale, and falls back to the upward normal (0,0,1) when the sample window is outside the 0..0x1ff range. Owner remains bounded to the saved CMonitor label; exact owner/layout, runtime terrain-normal behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("heightfield", "terrain-normal", "owner-provisional", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("heightfield_or_monitor", voidPtr),
                    param("out_normal", voidPtr),
                    param("world_pos", voidPtr)
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
    }
}
