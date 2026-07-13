# BattleEngine Morph Identity Canary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove, without executable or process-memory writes, that player-one
Transform input in a canonical copied Steam runtime reaches the expected
BattleEngine Morph, Move, and JetPart objects.

**Architecture:** Reuse the existing AppCore safe-copy, copied-options, managed
launch/stop, exact-window input, and CDB attach paths. Add a locked Stage A mode
that generates a private module-relative CDB command from the verified
executable, binds all runtime actions to one hash-bound process receipt, and
materializes only a strict public-safe control/positive/repeat summary.

**Tech Stack:** Python 3 standard library, PowerShell 5+/7, x86 CDB, existing
.NET 8 AppCore runtime services, JSON, SHA-256.

## Global Constraints

- Canonical executable: 2,506,752 bytes; SHA-256
  `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
- Controlled launch: `-skipfmv -level 850 -configuration 2`.
- Executable patch set is empty and
  `ApplyWindowedCompatibilityPatch=false`.
- Only copied `defaultoptions.bea` may be changed; player-one/runtime-P0
  `Actions/Transform` entry `0x21` is bound to Q.
- Runtime addresses are live `BEA` module base plus RVA. Preferred VAs are
  documentation only.
- Tracked files never contain executable bytes, generated fingerprint bytes,
  raw CDB logs, pointers, PIDs, HWNDs, absolute private paths, screenshots, or
  copied game files.
- CDB may use debugger-only hardware execution breakpoints and pseudo-registers.
  It may not write process memory or CPU registers, patch files, open a remote
  server, use `.shell`, or attach by process name.
- Stage A makes no timing, transition-duration, energy, shield, velocity,
  grounded, stall, handling, camera, gameplay, visual, audio, behavior-contract,
  or rebuild-parity claim.
- No Stage B sampler, Level 100 run, rebuild change, Ghidra mutation, release,
  tag, upload, installer, signing, or publication is part of this plan.
- Runtime execution requires an unexpired local authority baton and exclusive
  leases for `interactive-winui-desktop`, `bea-runtime`, `cdb-debugger`, and
  `local-proof-archive-write`.
- Use focused tests per task. Run one broad closeout after integration, not
  release-scale scans after each edit.

---

## File Map

Create:

- `tools/runtime_process_identity.psm1`: read and revalidate one private
  process/module/window receipt for CDB and input helpers.
- `tools/runtime_process_identity_test.py`: fake-process receipt tests without
  launching BEA.
- `tools/runtime-probes/battleengine-morph-identity-canary.cdb.tmpl`: tracked
  module-relative command template with no specimen bytes.
- `tools/battleengine_morph_identity_canary.py`: PE32 mapping, relocation-safe
  private command rendering, raw log parsing, strict run/matrix materialization,
  and public-summary validation.
- `tools/battleengine_morph_identity_canary_test.py`: synthetic PE, command,
  parser, claim-boundary, and matrix tests.
- `tools/run_battleengine_morph_identity_canary.py`: authority/lease validation,
  dry-run plan, and serialized control/positive/repeat execution.
- `tools/run_battleengine_morph_identity_canary_test.py`: fake-harness execution
  and cleanup tests.
- `tools/battleengine_morph_identity_authority.py`: shared exact private control
  schemas and path/hash/expiration validation used by both executor and harness.

Modify:

- `tools/start_cdb_server.ps1` and `tools/start_cdb_server_test.py`.
- `tools/send_game_window_input.ps1` and
  `tools/send_game_window_input_test.py`.
- `tools/winui_safe_copy_live_runtime_smoke.py` and
  `tools/winui_safe_copy_live_runtime_smoke_test.py`.
- `reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md`,
  `reverse-engineering/RE-INDEX.md`, `goal.md`, and state files only after an
  accepted runtime result.

Do not add a package script. These focused tools are invoked directly; the
contributor-facing command cleanup belongs to the separate validation campaign.

---

### Task 1: Private CDB Protocol And Strict Materializer

**Files:**
- Create: `tools/runtime-probes/battleengine-morph-identity-canary.cdb.tmpl`
- Create: `tools/battleengine_morph_identity_canary.py`
- Create: `tools/battleengine_morph_identity_canary_test.py`

**Interfaces:**
- Produces: `render_private_command(executable, template) -> RenderedCommand`.
- Produces: `validate_private_command(path, executable, template) -> RenderedCommand`.
- Produces: `materialize_run_bytes(live_artifact_bytes, cdb_log_bytes, role) -> dict`
  plus the path-based `materialize_run(...)` convenience wrapper.
- Produces: `materialize_matrix(runs) -> dict` and
  `validate_public_matrix(payload) -> None`.
- Consumes no AppCore or runtime process; all tests use synthetic files.

- [ ] **Step 1: Write failing PE and command-rendering tests**

```python
def test_render_uses_rvas_and_private_relocation_free_fingerprints(tmp_path):
    exe = build_pe32_fixture(
        tmp_path / "BEA.exe",
        image_base=0x00400000,
        executable_rvas=(0x000081C0, 0x0000A580, 0x00010C50, 0x000D3110),
        relocation_rvas=(0x000081D0,),
    )
    rendered = canary.render_private_command(exe, TEMPLATE)
    assert "BEA+0x000081c0" in rendered.text
    assert "BEA+0x0000a580" in rendered.text
    assert "0x004081c0" not in rendered.text
    assert rendered.fingerprint_size == 8
    assert all(not target.relocation_overlap for target in rendered.targets)
```

Also cover invalid DOS/PE headers, non-PE32 images, RVA outside an executable
section, truncated section data, relocation overlap, wrong specimen hash/size,
template drift, generated-command drift, and attempts to publish raw bytes.

- [ ] **Step 2: Run the test and confirm the missing module fails**

Run: `py -3 tools\battleengine_morph_identity_canary_test.py`

Expected: FAIL because `battleengine_morph_identity_canary` does not exist.

- [ ] **Step 3: Implement the PE32 and protocol types**

```python
CANONICAL_SIZE = 2_506_752
CANONICAL_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
P0_GLOBAL_RVA = 0x004A9D3C
PROBE_RVAS = {
    "playerTransformAction": 0x000D3110,
    "battleEngineMorph": 0x0000A580,
    "battleEngineMove": 0x000081C0,
    "jetPartMove": 0x00010C50,
}

@dataclass(frozen=True)
class ProbeFingerprint:
    event: str
    rva: int
    size: int
    sha256: str
    relocation_overlap: bool

@dataclass(frozen=True)
class RenderedCommand:
    text: str
    sha256: str
    template_sha256: str
    executable_sha256: str
    fingerprint_size: int
    targets: tuple[ProbeFingerprint, ...]
```

`Pe32Image` must parse section headers and the base-relocation directory with
`struct`, map RVA through section `VirtualAddress`/`PointerToRawData`, require
`IMAGE_SCN_MEM_EXECUTE`, and reject any 8-byte fingerprint intersecting a
`IMAGE_REL_BASED_HIGHLOW` relocation. Do not add `pefile` or another dependency.

- [ ] **Step 4: Implement the tracked template and exact renderer**

The template must contain only named placeholders and module-relative
expressions. The renderer substitutes private `by(BEA+RVA)==byte` conditions
from the verified executable. The generated command remains under
`local-proofs/`.

```text
.echo MORPH_CANARY_BEGIN
lm m BEA
r @$t0=0; r @$t1=0; r @$t2=0; r @$t3=0
.if ({{FINGERPRINT_CONDITION}}) { {{ARM_INPUT_BREAKPOINT}}; .echo MORPH_CANARY_READY; g } .else { .echo MORPH_CANARY_CODE_MISMATCH; qd }
```

The input breakpoint accepts only button `0x21` where `@ecx` equals
`poi(BEA+0x004a9d3c)`, stores `poi(@ecx+0x1c)` in debugger pseudo-register
`@$t3`, then arms at most three hardware execution breakpoints. Morph and Move
require `@ecx==@$t3`; JetPart requires `poi(@ecx+0x18)==@$t3`. Event output
contains equality booleans and raw `+0x260` dwords, not pointer values.

`validate_private_command` recomputes the exact rendered text and digest. It
does not implement a permissive new CDB grammar.

- [ ] **Step 5: Implement strict run and matrix schemas**

```python
RUN_ROLES = ("noInputControl", "positiveTransform", "positiveRepeat")
EXPECTED_EVENTS = (
    "playerTransformAction",
    "battleEngineMorph",
    "battleEngineMove",
    "jetPartMove",
)
PUBLIC_SCHEMA = "winui-original-binary-battleengine-morph-identity-canary.v1"
```

The public validator uses exact key sets at every object level. It permits only
RVA, region length/digests, raw `u32` hex, counts, event names/order, intra-run
equality booleans, source/copy unchanged booleans, receipt/raw-capture digests,
and cleanup outcomes. It rejects paths, filenames, module bases, preferred or
runtime VAs, pointers, PIDs, process times, HWNDs, log lines, code bytes,
screenshots, input timestamps, and cross-run pointer comparisons.

- [ ] **Step 6: Run focused tests**

Run: `py -3 tools\battleengine_morph_identity_canary_test.py`

Expected: PASS.

- [ ] **Step 7: Commit the protocol unit**

```powershell
git add tools\runtime-probes\battleengine-morph-identity-canary.cdb.tmpl tools\battleengine_morph_identity_canary.py tools\battleengine_morph_identity_canary_test.py
git commit -m "feat(re): add private morph canary protocol"
```

---

### Task 2: Receipt-Bound CDB And Input Safety

**Files:**
- Create: `tools/runtime_process_identity.psm1`
- Create: `tools/runtime_process_identity_test.py`
- Modify: `tools/start_cdb_server.ps1`
- Modify: `tools/start_cdb_server_test.py`
- Modify: `tools/send_game_window_input.ps1`
- Modify: `tools/send_game_window_input_test.py`

**Interfaces:**
- Produces: PowerShell `Assert-RuntimeProcessReceipt`.
- Consumes: private `runtime-process-receipt.v1` JSON plus its expected SHA-256.
- Produces: CDB helper result with debugger PID, start time, executable path,
  target receipt digest, command digest, and required-marker status.

- [ ] **Step 1: Write failing receipt tests**

Use a copied `cmd.exe` fixture process. Cover matching receipt, PID reuse/start
time mismatch, executable path/hash/size drift, manifest drift, module
path/base/size drift, second same-path process, HWND ownership mismatch, receipt
hash mismatch, and reparse receipt/command paths.

```python
def test_cdb_printonly_rejects_stale_receipt_start_time(self):
    receipt = self.write_receipt(started_at="2000-01-01T00:00:00Z")
    result = self.run_start_cdb(receipt=receipt, print_only=True)
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("start time", result.stderr.lower())
```

- [ ] **Step 2: Run the focused helpers and confirm failures**

```powershell
py -3 tools\runtime_process_identity_test.py
py -3 tools\start_cdb_server_test.py
py -3 tools\send_game_window_input_test.py
```

Expected: new tests FAIL.

- [ ] **Step 3: Implement the shared receipt validator**

```powershell
function Assert-RuntimeProcessReceipt {
    param(
        [string]$ReceiptPath,
        [string]$ExpectedReceiptSha256,
        [switch]$RequireWindow
    )
    # Parse exact schema, hash the receipt, inspect the exact PID, and compare
    # start time, executable, manifest, module, and optional HWND identity.
    # Return a PSCustomObject containing only the validated private receipt and
    # current Process object.
}
Export-ModuleMember -Function Assert-RuntimeProcessReceipt
```

The receipt is local-only and binds run ID, PID/start time, executable and
manifest path/hash/size, working directory, HWND, module path/base/size, launch
arguments, source/copy hashes, and command-template/generated-command digests.

- [ ] **Step 4: Harden CDB startup and ownership**

Add `-RuntimeReceiptPath`, `-ExpectedReceiptSha256`,
`-ExpectedCommandSha256`, and `-RequiredLogMarker`. Canary mode requires all
four. Add CDB arguments `-pd` and `-noshell`. Readiness means the required marker
appeared in the bounded log, not merely that the file exists.

The JSON result records CDB PID, CDB start time, CDB executable path, target
receipt digest, command digest, and marker status so cleanup can reject PID
reuse. Remote-server behavior remains disabled.

- [ ] **Step 5: Guarantee key release**

Wrap real key delivery in `try/finally`. Track every key successfully sent down
and issue an idempotent key-up in reverse order when any later action, focus
check, or helper step fails. Canary mode rejects `-AllowBackgroundWindowMessages`.

```powershell
$heldKeys = [System.Collections.Generic.List[object]]::new()
try {
    # Existing focused SendInput loop; append after each successful key-down and
    # remove after each successful key-up.
} finally {
    for ($index = $heldKeys.Count - 1; $index -ge 0; $index--) {
        $key = $heldKeys[$index]
        [void][GameWindowInputNative]::SendScanKey($key.scanCode, $true, $key.extended)
    }
}
```

- [ ] **Step 6: Run focused helper tests**

```powershell
py -3 tools\runtime_process_identity_test.py
py -3 tools\start_cdb_server_test.py
py -3 tools\send_game_window_input_test.py
```

Expected: PASS; no BEA or CDB process is launched by these tests.

- [ ] **Step 7: Commit the helper safety unit**

```powershell
git add tools\runtime_process_identity.psm1 tools\runtime_process_identity_test.py tools\start_cdb_server.ps1 tools\start_cdb_server_test.py tools\send_game_window_input.ps1 tools\send_game_window_input_test.py
git commit -m "fix(runtime): bind CDB and input to launch receipts"
```

---

### Task 3: Locked Stage A Mode In The Existing Live Harness

**Files:**
- Modify: `tools/winui_safe_copy_live_runtime_smoke.py`
- Modify: `tools/winui_safe_copy_live_runtime_smoke_test.py`

**Interfaces:**
- Consumes: exact private command renderer and receipt validator from Tasks 1-2.
- Produces: one private live artifact for one role.
- Does not decide the three-run matrix.

- [ ] **Step 1: Add failing protocol-mode tests**

```python
def test_morph_canary_protocol_is_unpatched_fixed_and_capture_free(self):
    args = parse("--runtime-protocol battleengine-morph-identity-canary-v1 --capture-count 0")
    plan = module.validate_runtime_protocol(args)
    self.assertEqual(plan.launch_arguments, ["-skipfmv", "-level", "850", "-configuration", "2"])
    self.assertEqual(plan.patch_keys, [])
    self.assertFalse(plan.apply_windowed_compatibility_patch)
    self.assertEqual(plan.transform_player1_token, "Q")
```

Also reject graphics/extra patches, music replacement, background messages,
wrong level/configuration, nonzero captures, arbitrary generated CDB commands,
missing marker, wrong specimen, and mixed proof levers.

- [ ] **Step 2: Run the harness test and confirm failure**

Run: `py -3 tools\winui_safe_copy_live_runtime_smoke_test.py`

Expected: new tests FAIL.

- [ ] **Step 3: Add one locked protocol option**

Add `--runtime-protocol` with choices `default` and
`battleengine-morph-identity-canary-v1`. In canary mode, derive every setting
from the protocol rather than exposing more independent CLI switches.

The generated C# runner must call AppCore with an empty patch set and:

```csharp
ApplyWindowedCompatibilityPatch: false
```

It must add only this copied-options override:

```csharp
new ConfigurationKeybindRow
{
    GroupLabel = "Actions",
    ActionLabel = "Transform",
    EntryId = 0x21,
    KeyboardDeviceCode = 8u,
    CurrentPlayer1Token = "",
    CurrentPlayer2Token = "",
    Player1Token = "Q",
    Player2Token = ""
}
```

An empty player-two token means no player-two override.

- [ ] **Step 4: Bind the private command and process receipt**

Canary mode permits a generated command only under the chosen ignored artifact
root. Re-render it from the canonical source and tracked template, require exact
text/digest equality, and pass the expected command and receipt digests to both
helpers.

After the exact window appears, write `runtime-process-receipt.v1` from the
managed process, actual main window, current `BEA` module, manifest, source/copy
hashes, and launch arguments. Revalidate immediately before CDB attach, input,
debugger cleanup, and managed stop.

- [ ] **Step 5: Make success and cleanup protocol-specific**

Canary mode allows `capture-count=0` and has no screenshot success dependency.
It requires the CDB ready marker, exact focused input for positive roles, copied
executable before/after canonical equality, ambient resource-root executable
before/after equality, effective override before/after canonical equality, CDB
identity-bound detach/exit, managed stop, and zero owned processes.

Cleanup order on every path is: release keys, end the exact owned CDB session
(`-pd` makes debugger exit detach), stop only the receipt-bound managed game
process, then census. Do not terminate an unknown BEA or CDB PID.

- [ ] **Step 6: Run focused integration tests**

```powershell
py -3 tools\battleengine_morph_identity_canary_test.py
py -3 tools\runtime_process_identity_test.py
py -3 tools\start_cdb_server_test.py
py -3 tools\send_game_window_input_test.py
py -3 tools\winui_safe_copy_live_runtime_smoke_test.py
```

Expected: PASS without launching BEA.

- [ ] **Step 7: Commit the live-harness unit**

```powershell
git add tools\winui_safe_copy_live_runtime_smoke.py tools\winui_safe_copy_live_runtime_smoke_test.py
git commit -m "feat(runtime): add locked morph identity canary mode"
```

---

### Task 4: Authority-Gated Three-Run Executor

**Files:**
- Create: `tools/battleengine_morph_identity_authority.py`
- Create: `tools/run_battleengine_morph_identity_canary.py`
- Create: `tools/run_battleengine_morph_identity_canary_test.py`
- Modify: `tools/winui_safe_copy_live_runtime_smoke.py`
- Modify: `tools/winui_safe_copy_live_runtime_smoke_test.py`
- Modify: `tools/battleengine_morph_identity_canary.py`
- Modify: `tools/battleengine_morph_identity_canary_test.py`

**Interfaces:**
- Consumes: one ignored authority JSON and one ignored lease JSON.
- Produces: three distinct private live artifacts, one private matrix manifest,
  and one sanitized matrix summary under the ignored proof root.
- Calls the existing live harness exactly once per role.

- [ ] **Step 1: Write failing dry-run, authority, and fake-harness tests**

```python
def test_matrix_order_is_fixed_and_live_requires_authority(tmp_path):
    executor = MatrixExecutor(fake_harness)
    with self.assertRaisesRegex(CanaryError, "authority"):
        executor.run_live(
            proof_root,
            missing_authority_path,
            leases_path,
            LIVE_ARM_PHRASE,
            source_root,
            exe_override,
        )
    plan = executor.dry_run(
        proof_root,
        authority_path,
        leases_path,
        source_root,
        exe_override,
    )
    assert [row.role for row in plan.runs] == [
        "noInputControl", "positiveTransform", "positiveRepeat"
    ]
```

Cover expiration, wrong action family, missing allowed/forbidden action,
nonzero spend, missing resource, conflicting owner, reparse proof root, run-order
drift, reused artifact/receipt/process identity, control transform hit, missing
positive event, pointer-equality failure, failed cleanup, and public-field leak.

- [ ] **Step 2: Run the test and confirm failure**

Run: `py -3 tools\run_battleengine_morph_identity_canary_test.py`

Expected: FAIL because the executor does not exist.

- [ ] **Step 3: Implement exact authority and lease schemas**

```python
ACTION_FAMILY = "copied-runtime-battleengine-identity-canary"
REQUIRED_RESOURCES = {
    "interactive-winui-desktop",
    "bea-runtime",
    "cdb-debugger",
    "local-proof-archive-write",
}
LIVE_ARM_PHRASE = "RUN BATTLEENGINE MORPH IDENTITY CANARY"
```

Require the allowed and forbidden action sets from the approved design, the
exact repo-root ignored `local-proofs/` boundary, cleanup/rollback, validation
gates, expiration, and `maxSpendUsd: 0`. Authority and lease files are distinct
siblings under a separate ignored control directory; they are never placed
inside the fresh matrix root. The executor and lower-level harness re-read and
hash-bind both controls before each live role. A dry run hash-binds the ambient
resource-root executable, validates the canonical effective in-root override,
and renders the private command, but does not launch a process or require the
live arm phrase. Live execution retains the ambient digest as a matrix-wide
baseline and revalidates it before every role and immediately before output
publication.

- [ ] **Step 4: Implement serialized role execution**

For each role, create a fresh child root and generated command, then invoke:

```text
py -3 tools/winui_safe_copy_live_runtime_smoke.py
  --runtime-protocol battleengine-morph-identity-canary-v1
  --canary-role <fixed role>
  --source-root <read-only resource root>
  --exe-override <canonical in-root BEA.exe or BEA.exe.original.backup>
  --artifact-root <private role root>
  --profiles-root <private role root>/app-config/OnslaughtCareerEditor/GameProfiles
  --canary-authority-file <private authority JSON>
  --expected-canary-authority-sha256 <digest>
  --canary-leases-file <private lease JSON>
  --expected-canary-leases-sha256 <digest>
  --arm-live-bea "LAUNCH SAFE COPY BEA"
```

The locked runtime protocol internally derives the generated CDB command,
observer attach, launch tuple, and role input; callers cannot supply those as
independent proof levers. The control sends no input. Each positive sends one
`tap:Q`. The executor waits for terminal cleanup and semantically materializes
each run in memory before starting the next role. It stops the matrix at the
first harness, identity, cleanup, or semantic failure.

- [ ] **Step 5: Publish the matrix only after all three roles pass**

Hash-bind each private artifact and raw CDB log, pass bounded immutable bytes to Task 1's
strict materializer, require distinct receipts/run IDs/processes/copied-profile
paths, and write the private manifest before publishing the sanitized summary
under the ignored root. Independent fresh runs may legitimately have identical
raw-log content; freshness is not inferred from differing capture digests. Do
not write into `reverse-engineering/` from the executor. An ordinary parent
console interrupt waits for the child harness to finish receipt-owned cleanup
and then invalidates the run; interrupted work never becomes accepted evidence.

- [ ] **Step 6: Run all focused non-live tests**

```powershell
py -3 tools\battleengine_morph_identity_canary_test.py
py -3 tools\run_battleengine_morph_identity_canary_test.py
py -3 tools\runtime_process_identity_test.py
py -3 tools\start_cdb_server_test.py
py -3 tools\send_game_window_input_test.py
py -3 tools\winui_safe_copy_live_runtime_smoke_test.py
git diff --check
```

Expected: PASS.

- [ ] **Step 7: Commit the executor unit**

```powershell
git add roadmap\battleengine-morph-identity-canary-implementation-plan-2026-07-12.md tools\battleengine_morph_identity_authority.py tools\run_battleengine_morph_identity_canary.py tools\run_battleengine_morph_identity_canary_test.py tools\battleengine_morph_identity_canary.py tools\battleengine_morph_identity_canary_test.py tools\winui_safe_copy_live_runtime_smoke.py tools\winui_safe_copy_live_runtime_smoke_test.py
git commit -m "feat(re): orchestrate morph identity canary matrix"
```

---

### Task 5: Execute Stage A And Close The Evidence Slice

**Files:**
- Local only: `local-proofs/battleengine-morph-identity-canary-control-*/authority.json`
- Local only: `local-proofs/battleengine-morph-identity-canary-control-*/leases.json`
- Local only fresh output: `local-proofs/battleengine-morph-identity-canary-matrix-*`
- Conditional create after PASS:
  `reverse-engineering/binary-analysis/battleengine-morph-identity-canary-runtime-summary-2026-07-12.json`
- Conditional create after PASS:
  `reverse-engineering/binary-analysis/battleengine-morph-identity-canary-runtime-summary-2026-07-12.md`
- Conditional mirror after PASS: matching two files under
  `lore-book/reverse-engineering/binary-analysis/`
- Conditional modify after PASS: movement crosswalk, RE indexes, `goal.md`, and
  state JSON files.

**Interfaces:**
- Consumes the tested executor and explicit local baton/leases.
- Produces either one accepted public-safe identity summary or one bounded
  blocker. It never produces a behavior contract or rebuild change.

- [ ] **Step 1: Create and validate local authority and lease records**

Populate every field named by the design, set zero spend and a short expiration,
record this task as owner, and verify no conflicting local lease or preexisting
BEA/CDB process exists. Keep both files ignored.

- [ ] **Step 2: Run the no-side-effect dry run**

```powershell
py -3 tools\run_battleengine_morph_identity_canary.py --proof-root local-proofs\battleengine-morph-identity-canary-matrix-20260712 --authority local-proofs\battleengine-morph-identity-canary-control-20260712\authority.json --leases local-proofs\battleengine-morph-identity-canary-control-20260712\leases.json --source-root <read-only-resource-root> --exe-override <read-only-resource-root>\BEA.exe.original.backup --dry-run
```

Expected: three fixed roles, a hash-bound ambient executable baseline, a
canonical effective override/copy identity, empty patch set, exact launch
arguments, private generated-command/AppConfig paths, and no process launch.

- [ ] **Step 3: Announce the native window and run the matrix hands-off**

```powershell
py -3 tools\run_battleengine_morph_identity_canary.py --proof-root local-proofs\battleengine-morph-identity-canary-matrix-20260712 --authority local-proofs\battleengine-morph-identity-canary-control-20260712\authority.json --leases local-proofs\battleengine-morph-identity-canary-control-20260712\leases.json --source-root <read-only-resource-root> --exe-override <read-only-resource-root>\BEA.exe.original.backup --arm-live "RUN BATTLEENGINE MORPH IDENTITY CANARY"
```

If user input or an unrelated process interferes, discard the affected run and
repeat it from a fresh copy. Do not relax an identity or event condition.

- [ ] **Step 4: Validate terminal cleanup and the sanitized summary**

```powershell
py -3 tools\battleengine_morph_identity_canary.py check --matrix local-proofs\battleengine-morph-identity-canary-matrix-20260712\battleengine-morph-identity-canary-sanitized-matrix.json
```

Expected: control has zero Transform/Morph hits; both positives have exact event
order and all intra-run equality booleans true; aggregate `sourceUnchanged` and
`copyUnchanged` are true after the private comparisons; the matrix-wide ambient
baseline still matches; and keys, CDB, and managed game process are clean.

- [ ] **Step 5: Apply the evidence decision**

If any acceptance condition fails, keep raw material private, release leases,
record the exact blocker in `goal.md` and state, and stop before Stage B.

If all pass, copy only the validated sanitized JSON into the canonical and Lore
paths, add a concise Markdown interpretation/nonclaim note, link it from the RE
indexes, and update copied-runtime confidence only for call-chain identity.
Do not promote timing, field semantics, gameplay, parity, or rebuild readiness.

- [ ] **Step 6: Run one integrated closeout**

```powershell
py -3 tools\battleengine_morph_identity_canary_test.py
py -3 tools\run_battleengine_morph_identity_canary_test.py
py -3 tools\runtime_process_identity_test.py
py -3 tools\start_cdb_server_test.py
py -3 tools\send_game_window_input_test.py
py -3 tools\winui_safe_copy_live_runtime_smoke_test.py
npm test
npm run test:docsync
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
Get-Content -Raw developer_agent_state.json,documentation_agent_state.json | ConvertFrom-Json | Out-Null
git diff --check
```

This is the one broad closeout for the substantive runtime slice. Do not run
the public allowlist or hygiene scans separately beforehand.

- [ ] **Step 7: Review, commit, push, and release leases**

Use one normal/adversarial review envelope for the implemented diff and
sanitized result. Fix concrete blockers, commit the accepted closeout, push
`main`, verify local/origin/live equality with divergence `0 0`, mark local
leases released, and confirm no BEA/CDB process remains. Do not publish a
release or tag.

---

## Plan Self-Review

- Spec coverage: Stage A safe copy, identity, fingerprint, input, CDB, private
  evidence, public materialization, cleanup, authority, controls, repeat, and
  nonclaims each map to a task.
- Scope: Stage B, Level 100, and rebuild behavior are intentionally excluded.
- Type consistency: Tasks 3-4 consume the exact renderer/materializer and
  receipt interfaces created in Tasks 1-2.
- Placeholder scan: no placeholder markers, unspecified error handling, or
  generic test-writing step remains.
- Ceremony check: no package script, hosted CI, AppCore product API, screenshot
  dependency, recursive proof-plan chain, or per-edit full-tree suite is added.
