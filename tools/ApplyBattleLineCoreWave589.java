//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyBattleLineCoreWave589 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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
        sb.append(spec.returnType.getDisplayName());
        sb.append(" ");
        sb.append(spec.callingConvention);
        sb.append(" ");
        sb.append(spec.name);
        sb.append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName());
            sb.append(" ");
            sb.append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "battleline-core-wave589",
            "retail-binary-evidence",
            "battleline",
            "dx-render",
            "signature-corrected",
            "comment-hardened"
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
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
        if (!signatureMatches(fn, spec)) {
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
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
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
                println("MISSING: " + spec.address);
                stats.missing++;
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    stats.wouldRename++;
                    stats.skipped++;
                    return;
                }
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (!needsUpdate(fn, spec)) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }
            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType charType = CharDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0053a050",
                "CDXBattleLine__Constructor",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("origin_x", intType), param("origin_y", intType) },
                "Wave589 signature/comment hardening: RET 0x8 and the CHud__Init callsite show an ECX HUD battleline field block plus two stack constants (-7, 14). The body stores them at this+0x64/+0x68, allocates a 0x158 texture-backed CDXBattleLine/CDXSurf object, installs vtable 0x005e4f64, creates the line texture as 128x1 or 128x128, and calls InitMipLevels. Static retail evidence only; exact source identity/layout, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__Constructor"},
                tags("constructor", "ret-8", "hud-field-block", "vtable-005e4f64")
            ),
            new Spec(
                "0x0053a120",
                "CDXBattleLine__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("delete_flags", byteType) },
                "Wave589 signature/comment hardening: vtable slot 0x005e4f64[0] and RET 0x4 show a scalar deleting destructor wrapper. The body calls the local CDXBattleLine destructor thunk, frees this through the OID/CDX memory manager when delete_flags bit 0 is set, and returns this. Static retail evidence only; exact source identity/layout, runtime teardown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__scalar_deleting_dtor"},
                tags("scalar-deleting-dtor", "vtable-slot", "ret-4")
            ),
            new Spec(
                "0x0053a140",
                "CDXBattleLine__DestructorThunk",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave589 name/signature/comment hardening: one-instruction JMP thunk to the real CDXSurf__dtor at 0x00556d90, reached from CDXBattleLine__scalar_deleting_dtor. This corrects the stale duplicate CDXSurf__dtor label at 0x0053a140 while preserving the base-destructor evidence. Static retail evidence only; CDXBattleLine-specific teardown beyond the base CDXSurf cleanup, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXSurf__dtor", "CDXBattleLine__DestructorThunk"},
                tags("destructor-thunk", "jmp-thunk", "base-cdxsurf-dtor", "renamed")
            ),
            new Spec(
                "0x0053a150",
                "CDXBattleLine__LoadTextures",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave589 signature/comment hardening: ECX-only loader reached from CHud__LoadTextures after the HUD battleline pointer at CHud+0x30 is loaded. The body finds hud\\marker.tga, creates the 500-entry dynamic overlay vertex buffer at this+0x78, finds hud\\V2\\BattleEngineMarker.tga, allocates the overlay CTexture at this+0x08, and creates its 128x128 surface. Static retail evidence only; exact asset ownership/layout, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__LoadTextures"},
                tags("load-textures", "hud-textures", "dynamic-vbuffer", "ecx-only")
            ),
            new Spec(
                "0x0053a280",
                "CDXBattleLine__Setup",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave589 signature/comment hardening: ECX-only setup target reached by the CHud__PostLoadProcess JMP after loading CHud+0x30. The body temporarily forces DAT_00889010, marks state byte this+0x24 as 2, calls CDXBattleLine__BuildMesh, restores the global, and returns 1. Static retail evidence only; exact initialization contract, runtime mesh readiness behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__Setup"},
                tags("setup", "post-load", "build-mesh", "ecx-only")
            ),
            new Spec(
                "0x0053a390",
                "CDXBattleLine__UpdateHeightmap",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave589 signature/comment hardening: ECX-only heightmap updater reached from BuildMesh and the raw 0x0053a010 trampoline. The body uses the texture/frame at this+0x08, recomputes heightfield extents, locks the mip/heightmap surface, samples a bounded circular terrain area, writes short intensity values, and unlocks the surface. Static retail evidence only; exact terrain/layout semantics, runtime heightmap behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__UpdateHeightmap"},
                tags("heightmap", "terrain-sampling", "ecx-only")
            ),
            new Spec(
                "0x0053a5e0",
                "CDXBattleLine__BuildMesh",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave589 signature/comment hardening: ECX-only battleline mesh builder reached from Setup. The body calls UpdateHeightmap, allocates a separate 0x18-byte Triangulate work object, creates the quad mesh, inserts influence/unit points, relaxes edges, stores vertex/triangle counts at this+0x1c/+0x20, and creates vertex/index buffers. Static retail evidence only; exact mesh layout, runtime triangulation behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__BuildMesh"},
                tags("build-mesh", "triangulate-work-object", "vertex-index-buffer", "ecx-only")
            ),
            new Spec(
                "0x0053a930",
                "CDXBattleLine__InitMipLevels",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave589 signature/comment hardening: ECX-only mip initializer reached from the constructor and the raw 0x0053a010 trampoline. The body gets the animated texture frame from this+0x04, iterates mip levels, locks each level, writes the observed short gradient bands, and unlocks. Static retail evidence only; exact texture format/layout, runtime visual result, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__InitMipLevels"},
                tags("mip-levels", "texture-gradient", "ecx-only")
            ),
            new Spec(
                "0x0053aa40",
                "CDXBattleLine__UpdateVertexBuffer",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("hud_y", floatType), param("use_unit_marker_offsets", intType) },
                "Wave589 signature/comment hardening: RET 0x8 and two CDXBattleLine__Render callsites show ECX=this plus hud_y and a mode flag stack pair. The body locks the vertex buffer at this+0x70, emits the eight base marker records through SetupVertex, walks the active unit list for additional marker records, and unlocks the buffer. Static retail evidence only; exact marker layout, runtime unit-marker behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__UpdateVertexBuffer"},
                tags("update-vertex-buffer", "ret-8", "marker-vertices")
            ),
            new Spec(
                "0x0053ab40",
                "CDXBattleLine__SetupVertex",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("out_vertex", floatPtr),
                    param("screen_base_y", floatType),
                    param("screen_offset_x", floatType),
                    param("screen_offset_y", floatType),
                    param("source_xy", floatPtr),
                    param("intensity", floatType),
                    param("mode", charType)
                },
                "Wave589 signature/comment hardening: cdecl helper confirmed by two UpdateVertexBuffer callsites that push seven arguments and then add ESP,0x1c. The body writes one 0x20-byte marker vertex/UV/intensity record, using source_xy scaling for mode 0 and alternate UV/intensity fields for nonzero mode. Static retail evidence only; exact vertex struct names, runtime marker rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__SetupVertex"},
                tags("setup-vertex", "cdecl", "marker-vertex-record")
            ),
            new Spec(
                "0x0053abe0",
                "CDXBattleLine__Render",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave589 signature/comment hardening: ECX-only render method reached from CHud__RenderBattleline after the HUD battleline pointer at CHud+0x30 is loaded. The body gates on the influence map, computes HUD Y placement, updates marker vertices in two modes, runs layered indexed-primitive passes with battleline textures, calls RenderTriOverlayPass, and draws BattleEngine marker sprites. Static retail evidence only; exact pass semantics, runtime visual behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__Render"},
                tags("render", "hud-battleline", "multi-pass", "ecx-only")
            ),
            new Spec(
                "0x0053b470",
                "CDXBattleLine__RenderTriOverlayPass",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave589 signature/comment hardening: ECX-only helper called by CDXBattleLine__Render after base battleline passes. The body unlocks the dynamic overlay buffer if it is still locked, binds the marker texture at this+0x0c, sets render state for two overlay draws, and submits this+0x60 vertices from the buffer at this+0x78 when the count is nonzero. Static retail evidence only; exact overlay semantics, runtime visual behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__RenderTriOverlayPass"},
                tags("overlay-pass", "dynamic-vbuffer", "ecx-only")
            ),
            new Spec(
                "0x0053b5f0",
                "CDXBattleLine__AppendOverlayVertex",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("world_x", floatType), param("world_y", floatType), param("color_rgb", uintType) },
                "Wave589 signature/comment hardening: RET 0xc and the PopulateBattleLineAndInfluenceOverlayVertices callsites prove ECX=this plus three stack arguments: world_x, world_y, and color_rgb constants 0xffff00/0xff0808. The body lazily locks the dynamic overlay buffer, computes a pulsing color boost at this+0x58, projects the world point into HUD space, writes one 0x14-byte overlay vertex, and increments this+0x60 up to 500. Static retail evidence only; exact overlay vertex layout, runtime marker behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__AppendOverlayVertex"},
                tags("append-overlay-vertex", "ret-0xc", "dynamic-vbuffer", "color-rgb")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
