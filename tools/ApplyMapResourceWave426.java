//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMapResourceWave426 extends GhidraScript {
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "map-resource-wave426",
            "terrain-heightfield",
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
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0047e870",
                "CHeightField__ResetCoreBuffersAndFlags",
                "__fastcall",
                voidPtr,
                "Wave426 owner/signature/comment correction: supersedes the older CUnitAI owner label after MAP/heightfield singleton evidence from the 0x006fadc8 constructor and map-load cluster. Clears +0x20/+0x24, zeroes 1024 dwords at +0x28, clears the +0x1028 owned buffer pointer, and returns this. Static retail evidence only; HeightField.cpp/world.cpp are absent from the current Stuart snapshot, and concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ResetWorkGrid1024AndFlags"},
                tags("heightfield", "constructor-helper", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047e8a0",
                "CHeightField__FreeOwnedBuffers_24_1028",
                "__fastcall",
                voidType,
                "Wave426 owner/signature/comment correction: supersedes the older CUnitAI owner label after MAP/heightfield singleton evidence. Frees owned buffers at +0x24 and +0x1028 through OID__FreeObject and clears each slot after the free. Static retail evidence only; concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__FreeOwnedObjects_24_1028", "CHeightField__FreeOwnedBuffers_24_1028"},
                tags("heightfield", "owned-buffer-free", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047ea20",
                "CHeightField__GetHeightSamplePacked16",
                "__fastcall",
                uintType,
                "Wave426 owner/signature/comment correction: supersedes the older provisional CWorld owner label after the map/heightfield min-max table builder xref. Samples packed 16-bit height data through +0x1028 using packed X/Z coordinates with edge branches around 0x200 and 0xa1ffe. Static retail evidence only; concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CWorld__GetHeightSamplePacked16"},
                tags("heightfield", "packed-height-sample", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x_packed", uintType),
                    param("z_packed", uintType)
                }
            ),
            new Spec(
                "0x00490900",
                "Vec3__SubtractInPlace",
                "__thiscall",
                voidType,
                "Wave426 signature/comment correction: RET 0x4 confirms one rhs_vector stack argument, and the body subtracts rhs_vector from this across three float components in place. Static retail evidence only; exact source identity, runtime vector behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("vector-math", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs_vector", voidPtr)
                }
            ),
            new Spec(
                "0x00490a40",
                "CHeightField__TraceLineAgainstHeightfield",
                "__thiscall",
                intType,
                "Wave426 owner/signature/comment correction: corrects the older CStaticShadows owner label to heightfield/MAP evidence. RET 0xc confirms line, hit_out, and stop_at_height_limit stack arguments; the body checks +0x13dc/+0x13e0 min/max cells and falls back to CHeightField__SampleInterpolatedHeight before writing the hit output. Static retail evidence only; concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CStaticShadows__TraceSegmentAgainstHeightfield"},
                tags("heightfield", "line-trace", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("line", voidPtr),
                    param("hit_out", voidPtr),
                    param("stop_at_height_limit", intType)
                }
            ),
            new Spec(
                "0x00490e10",
                "CHeightField__Constructor",
                "__fastcall",
                voidPtr,
                "Wave426 owner/signature/comment correction: global MAP constructor wrapper calls CHeightField__ResetCoreBuffersAndFlags and returns this. Static retail evidence only; source HeightField.cpp is absent, and concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__InitWorkGrid1024"},
                tags("heightfield", "constructor", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00490e20",
                "CHeightField__FreeOwnedBuffers_Thunk",
                "__fastcall",
                voidType,
                "Wave426 owner/signature/comment correction: global MAP destructor thunk tail-calls CHeightField__FreeOwnedBuffers_24_1028. Static retail evidence only; concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__FreeOwnedObjects_24_1028", "CHeightField__FreeOwnedBuffers_24_1028"},
                tags("heightfield", "destructor-thunk", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00490e30",
                "CHeightField__BuildCellMinMaxHeightTable",
                "__fastcall",
                voidType,
                "Wave426 owner/signature/comment correction: corrects the older CGame owner label because CGame::PostLoadProcess calls MAP.InitQuickCollisionMap and the body operates on the heightfield singleton. Builds the 9x9 cell min/max table rooted at +0x13dc using +0x102c scale and CHeightField__GetHeightSamplePacked16. Static retail evidence only; concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__BuildCellMinMaxHeightTable"},
                tags("heightfield", "minmax-table", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00490f10",
                "CHeightField__InitAndClearMapLoadFlags",
                "__fastcall",
                intType,
                "Wave426 owner/signature/comment correction: source CGame::Init MAP.Init context; the retail body initializes this map/heightfield context then clears map-load flags at +0x93e0/+0x93e4 and returns TRUE/FALSE. Static retail/source-context evidence only; concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__InitMapLoadStateFlags"},
                tags("heightfield", "map-init", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00490f40",
                "CHeightField__ShutdownAndDestroyMixerMap",
                "__fastcall",
                voidType,
                "Wave426 owner/signature/comment correction: corrects the older CUnitAI owner label because the shutdown caller sits in CGame shutdown MAP.Shutdown context. The body calls CHeightField__FreeOwnedBuffers_24_1028, then tail-calls CMixerMap__Destroy for the same map/heightfield object. Static retail/source-context evidence only; concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap"},
                tags("heightfield", "map-shutdown", "mixer-map", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00490f50",
                "CHeightField__TraceMapLoadRequestAndCheckLoadedFlags",
                "__thiscall",
                intType,
                "Wave426 owner/signature/comment correction: corrects the older CWorld owner label because CWorld__LoadWorld passes the MAP/heightfield singleton at 0x006fadc8. RET 0xc confirms map_number, load_geometry, and load_properties stack arguments; the body traces Loading map %d and checks +0x93e0/+0x93e4 loaded flags. Static retail evidence only; concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CWorld__CanLoadMapSection"},
                tags("heightfield", "map-load-flags", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("map_number", intType),
                    param("load_geometry", intType),
                    param("load_properties", intType)
                }
            ),
            new Spec(
                "0x00491060",
                "CHeightField__DeserializeMapAndInitResources",
                "__thiscall",
                voidType,
                "Wave426 owner/signature/comment correction: corrects the older CResourceAccumulator owner label because CEngine__Deserialize source MAP.Deserialize context follows CMapTex deserialization. The body reads map metadata from chunk_reader, marks +0x93e0/+0x93e4 loaded, calls CHeightField__Load, calls CMixerMap__Init, and drives CEngine__LoadMixers plus sky/water resource setup. Static retail/source-context evidence only; concrete layout, runtime terrain behavior, and rebuild parity remain unproven.",
                new String[] {"CResourceAccumulator__DeserializeMapAndInitResources"},
                tags("heightfield", "map-deserialize", "resource-init", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("chunk_reader", voidPtr)
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
