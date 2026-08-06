//@category Symbol
//
// Read-only openability probe for `tools/ghidra_project_backup.py verify`.
//
// The backup tool's `verify` subcommand copies a project pair to scratch, opens
// it with `-readOnly -noanalysis`, and requires this script to emit
//
//     GHIDRA_PROJECT_OPEN_PROBE_OK program=<name> md5=<md5> sha256=<sha256> functions=<count>
//
// on stdout.  Anything else - a missing sentinel, a nonzero exit, or any content
// drift in the probed copy - fails the verification closed.
//
// The script that this contract names was absent from the repository, so
// `verify` could not pass for any backup.  A backup that has only been hashed is
// not a backup that is known to open; this restores the second half of that
// check.  It reads nothing, writes nothing, and asserts the program name plus
// both executable digests Ghidra recorded at import time.  The measured
// function count is included in the single success sentinel so a receipt can
// distinguish an observed reopen from an echoed expectation.
//
// Usage (issued by the Python tool, not by hand):
//     -postScript GhidraProjectOpenProbe.java <programName> <expectedMd5> <expectedSha256>

import ghidra.app.script.GhidraScript;

public class GhidraProjectOpenProbe extends GhidraScript {

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 3) {
            System.out.println("GHIDRA_PROJECT_OPEN_PROBE_FAIL reason=usage"
                + " expected=<programName> <expectedMd5> <expectedSha256>");
            return;
        }
        String expectedProgram = args[0];
        String expectedMd5 = args[1].toLowerCase();
        String expectedSha256 = args[2].toLowerCase();

        if (currentProgram == null) {
            System.out.println("GHIDRA_PROJECT_OPEN_PROBE_FAIL reason=no_current_program");
            return;
        }

        String actualProgram = currentProgram.getName();
        if (!expectedProgram.equals(actualProgram)) {
            System.out.println("GHIDRA_PROJECT_OPEN_PROBE_FAIL reason=program_name_mismatch"
                + " expected=" + expectedProgram + " actual=" + actualProgram);
            return;
        }

        String actualMd5 = currentProgram.getExecutableMD5();
        actualMd5 = actualMd5 == null ? "" : actualMd5.toLowerCase();
        if (!expectedMd5.isEmpty() && !expectedMd5.equals(actualMd5)) {
            System.out.println("GHIDRA_PROJECT_OPEN_PROBE_FAIL reason=md5_mismatch"
                + " expected=" + expectedMd5 + " actual=" + actualMd5);
            return;
        }

        String actualSha256 = currentProgram.getExecutableSHA256();
        actualSha256 = actualSha256 == null ? "" : actualSha256.toLowerCase();
        if (!expectedSha256.equals(actualSha256)) {
            System.out.println("GHIDRA_PROJECT_OPEN_PROBE_FAIL reason=sha256_mismatch"
                + " expected=" + expectedSha256 + " actual=" + actualSha256);
            return;
        }

        // Touch the listing so the probe proves the database is readable, not
        // merely that the project directory could be latched.
        long functionCount = currentProgram.getFunctionManager().getFunctionCount();
        System.out.println("GHIDRA_PROJECT_OPEN_PROBE_OK program=" + actualProgram
            + " md5=" + actualMd5
            + " sha256=" + actualSha256
            + " functions=" + functionCount);
    }
}

