//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyParticleManagerOwnerLinksWave822 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "particle-manager-owner-links-wave822",
            "wave822-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "particle-manager",
            "owner-link"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        return new Spec[] {
            new Spec(
                "0x004caf30",
                "CParticleManager__ClearParticleOwnerBacklinks",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave822 static read-back/signature hardening: no-argument helper walks the global effect-handle chain at DAT_0082b3e4 and clears each handle's observed owner activity/backlink fields at +0xa4/+0xa8 before cleanup/prune passes. Xrefs are CGame__ShutdownRestartLoop, CDXEngine__ShutdownParticleSystemBundle, and CFrontEnd__ReleaseParticleHudWaypointResources. Static retail Ghidra evidence only; exact handle/owner-link layouts, runtime particle shutdown behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("effect-handle", "shutdown-cleanup")
            ),
            new Spec(
                "0x004cb040",
                "ParticleEffectLink__PushGlobalList",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("link_node", voidPtr)
                },
                "Wave822 static read-back/name/signature correction: ECX carries link_node; the body stores the old DAT_0082b3e8 head at link_node+0 and then makes link_node the new global effect/owner-link head. This replaces the older CWorldPhysicsManager-only label and cdecl stack-argument signature, which are too narrow because xrefs span unit/object/projectile/render/effect creation paths and the function reads no stack parameter. Static retail Ghidra evidence only; exact link-node owner type, allocation ownership, runtime particle/effect behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("global-list", "effect-owner-link", "name-corrected")
            ),
            new Spec(
                "0x004cb080",
                "CParticleManager__PruneDeadOwnerLinks",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave822 static read-back/signature hardening: no-argument helper walks the DAT_0082b3e8 effect/owner-link node chain and clears link_node+0x4 when the linked effect handle's activity flag at +0xa4 has been cleared. Xrefs pair it with CParticleManager__ClearParticleOwnerBacklinks in game shutdown, DX particle-bundle shutdown, and frontend particle/HUD waypoint release paths. Static retail Ghidra evidence only; exact link-node layout, runtime shutdown behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("global-list", "owner-link-prune", "shutdown-cleanup")
            ),
            new Spec(
                "0x004cbc60",
                "CParticleManager__UpdateRenderNodesAndResetState",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave822 static read-back/signature hardening: no-argument render-node helper walks DAT_0082b404 via node+0x40, calls vfunc +0x4 to identify observed type 0xb nodes, calls vfunc +0x5c with argument 0 for those nodes, then restores render-state slot 0xf to 1 through RenderState_Set. Xrefs are CDXEngine__Render and CDXFrontEnd__SetupRenderMatricesAndProjection. Static retail Ghidra evidence only; exact render-node type identity, runtime render behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("render-node", "render-state")
            )
        };
    }

    private boolean hasTags(Function fn, String[] expected) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.expectedName)) {
            return false;
        }
        if (!fn.getSignature().getReturnType().isEquivalent(spec.returnType)) {
            return false;
        }
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (!fn.getParameter(i).getName().equals(spec.parameters[i].getName())) {
                return false;
            }
            if (!fn.getParameter(i).getDataType().isEquivalent(spec.parameters[i].getDataType())) {
                return false;
            }
        }
        return true;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.expectedName)) {
            if (dryRun) {
                println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.expectedName);
                stats.wouldRename++;
            } else {
                fn.setName(spec.expectedName, SourceType.USER_DEFINED);
                println("RENAMED: " + spec.address + " " + spec.expectedName);
                stats.renamed++;
            }
        }

        boolean signatureOk = sameSignature(fn, spec);
        boolean commentOk = spec.comment.equals(fn.getComment());
        boolean tagsOk = hasTags(fn, spec.tags);
        if (signatureOk && commentOk && tagsOk) {
            println("SKIP: " + spec.address + " " + spec.expectedName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY_UPDATE: " + spec.address + " " + spec.expectedName
                + " signature_ok=" + signatureOk + " comment_ok=" + commentOk + " tags_ok=" + tagsOk);
            if (!signatureOk) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.skipped++;
            return;
        }

        if (!signatureOk) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        } else {
            stats.commentOnlyUpdated++;
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getSignature());
            stats.bad++;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            stats.bad++;
        }
        if (!hasTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            stats.bad++;
        }
        if (stats.bad == 0) {
            println("READBACK_OK: " + spec.address + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0] : "dry";
        boolean dryRun = isDryRun(mode);
        println("ApplyParticleManagerOwnerLinksWave822 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
