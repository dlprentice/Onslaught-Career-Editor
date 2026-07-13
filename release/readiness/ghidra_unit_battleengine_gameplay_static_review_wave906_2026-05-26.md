# Ghidra Unit / BattleEngine / Gameplay Static Review Wave906 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static review evidence
Date: 2026-05-26
Scope: `unit-battleengine-gameplay-static-review-wave906`

Wave906 is a read-only post-100 system review. It makes no Ghidra metadata mutation, no executable-byte change, no save mutation, and no BEA launch. The wave records a `static-coherent Unit/BattleEngine/gameplay core` after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`.

Evidence summary:

- Selected function rows: `633` rows across `75` families, all commented and clean-signature.
- Cluster counts: Unit core / AI / squads `199`, BattleEngine player state `133`, weapons / rounds / targeting `106`, unit subclasses / guides `102`, damage / destruction / spawn `93`.
- Large family anchors: `CUnit` `90`, `CUnitAI` `63`, `CBattleEngine` `47`, `CSquadNormal` `31`, `CBattleEngineWalkerPart` `27`, `CBattleEngineJetPart` `23`, `CGeneralVolume` `23`, `CDestructableSegmentsController` `19`, `CCollisionSeekingRound` `17`, `CSpawnerThng` `14`, `CRound` `13`, and `CWeapon` `12`.
- Representative functions: `CUnit__ApplyDamage`, `CUnitAI__UpdateActivationStateAndSpawnPickup`, `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`, `CBattleEngine__AddProjectile`, `CBattleEngine__Morph`, `CBattleEngine__HandleCloak`, `CBattleEngine__AugmentWeapon`, `CBattleEngineJetPart__WeaponFired`, `CBattleEngineWalkerPart__WeaponFired`, `CWeapon__HandleFireBurstEvent`, `CRound__SpawnConfiguredProjectile`, `CSpawnerThng__DoSpawn`, and `CDestroyableSegment__VFunc_03_ApplyDamage`.
- Verified read-only Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

What this proves:

- The selected Unit/BattleEngine/gameplay owner-family rows are closed under the current function-quality proxy.
- The public docs now review unit lifecycle, AI/deploy/activation helpers, BattleEngine mode/weapon/target/projectile paths, weapon/round config loaders, projectile collision-seeking, squad targeting, spawner waves, concrete unit subclass guide rows, and destructible segment damage handling as one static system slice.
- The claim is static coherence, not runtime gameplay behavior.

What remains unproven:

- Exact concrete object layouts.
- Runtime damage, AI, weapon, input, mode-switching, targeting, spawn, and projectile behavior.
- Runtime mission/gameplay outcomes.
- BEA patch behavior.
- Clean-room rebuild parity.
