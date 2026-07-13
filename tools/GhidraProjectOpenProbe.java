//@category Analysis

import ghidra.app.script.GhidraScript;

public class GhidraProjectOpenProbe extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 1 || args.length > 2 ||
                args[0] == null || args[0].trim().isEmpty()) {
            throw new IllegalArgumentException("expected program name and optional executable MD5");
        }
        String expected = args[0].trim();
        if (currentProgram == null) {
            throw new IllegalStateException("no current program");
        }
        if (!expected.equals(currentProgram.getName())) {
            throw new IllegalStateException(
                "unexpected program: expected=" + expected + " actual=" + currentProgram.getName()
            );
        }
        String actualMd5 = currentProgram.getExecutableMD5();
        if (args.length == 2) {
            String expectedMd5 = args[1].trim().toLowerCase();
            if (actualMd5 == null || !expectedMd5.equals(actualMd5.toLowerCase())) {
                throw new IllegalStateException(
                    "unexpected executable MD5: expected=" + expectedMd5 + " actual=" + actualMd5
                );
            }
        }
        println(
            "GHIDRA_PROJECT_OPEN_PROBE_OK program=" + expected +
            (args.length == 2 ? " md5=" + actualMd5.toLowerCase() : "")
        );
    }
}
