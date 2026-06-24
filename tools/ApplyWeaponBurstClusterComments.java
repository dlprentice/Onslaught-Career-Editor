//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class ApplyWeaponBurstClusterComments extends GhidraScript {

    private static class Target {
        final String address;
        final String expectedName;
        final String comment;

        Target(String address, String expectedName, String comment) {
            this.address = address;
            this.expectedName = expectedName;
            this.comment = comment;
        }
    }

    private static final Target[] TARGETS = new Target[] {
        new Target(
            "0x00506930",
            "CWeapon__HandleFireBurstEvent",
            "Weapon table event handler for burst event 0x1389. Calls the current-preset projectile-burst body and reschedules follow-up burst events.\n"
          + "Behavior-backed event-handler label only; not exact source CWeapon::Fire or CBattleEngine::WeaponFired identity, and not runtime stealth proof."
        ),
        new Target(
            "0x00505f70",
            "CWeapon__scalar_deleting_dtor",
            "Scalar deleting destructor shape for the weapon object: detaches/shuts down monitoring, then conditionally frees the object.\n"
          + "Destructor evidence only; not weapon-fire or stealth behavior proof."
        ),
        new Target(
            "0x005069f0",
            "CEngine__SpawnProjectileBurstFromCurrentPreset",
            "Inner projectile-burst body reached from CWeapon__HandleFireBurstEvent and CGeneralVolume__SpawnBurstFromPresetWithFallback.\n"
          + "Creates projectiles from the current preset, resolves target/list entries, and updates burst/cooldown state. Owner/name remains provisional; source CWeapon::Fire, CBattleEngine::WeaponFired, and runtime stealth behavior remain unproven."
        ),
        new Target(
            "0x00506010",
            "CGeneralVolume__SpawnBurstFromPresetWithFallback",
            "Shared preset fallback dispatcher: resolves a percent/bucket preset, gates cooldown, clears owner state when applicable, calls the current-preset projectile-burst body, plays optional sample, and schedules event 0x1389 follow-up.\n"
          + "Direct callers include UnitAI, Sentinel, CEngine wrapper, and CGeneralVolume paths; current owner/name is provisional and not source weapon-fire identity."
        )
    };

    private static boolean isDryRun(String mode) {
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

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        int applied = 0;
        int skipped = 0;
        int missing = 0;
        int bad = 0;

        for (Target target : TARGETS) {
            Function fn;
            try {
                fn = getFunctionOrThrow(target.address);
            } catch (Exception ex) {
                println("MISSING: " + target.address + " " + ex.getMessage());
                missing++;
                continue;
            }

            String actualName = fn.getName();
            if (!target.expectedName.equals(actualName)) {
                println("BADNAME: " + target.address + " expected " + target.expectedName + " actual " + actualName);
                bad++;
                continue;
            }

            if (dryRun) {
                println("DRY: " + target.address + " " + actualName);
                skipped++;
                continue;
            }

            fn.setComment(target.comment);
            println("OK: " + target.address + " " + actualName);
            applied++;
        }

        println("--- SUMMARY ---");
        println("applied=" + applied + " skipped=" + skipped + " missing=" + missing + " bad=" + bad);
    }
}
