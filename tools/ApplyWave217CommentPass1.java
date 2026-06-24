//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;

public class ApplyWave217CommentPass1 extends GhidraScript {

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Function fn = getFunctionAt(toAddr(addrText));
        if (fn == null) {
            Function cf = getFunctionContaining(toAddr(addrText));
            if (cf != null && cf.getEntryPoint().equals(toAddr(addrText))) {
                fn = cf;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private void setFnComment(String addr, String c) throws Exception {
        Function fn = getFunctionOrThrow(addr);
        fn.setComment(c);
    }

    @Override
    protected void run() throws Exception {
        int updated = 0;

        setFnComment(
            "0x0040acc0",
            "Selects an aim target candidate and may enqueue follow-up event payload reads.\n"
          + "Used in battle-engine targeting paths; signature normalized in wave217 pass1."
        );
        updated++;

        setFnComment(
            "0x0047eff0",
            "Blits a landscape tile region with lighting-mask/culling parameters into destination buffer stride.\n"
          + "High-arity render helper used by landscape texture composition."
        );
        updated++;

        setFnComment(
            "0x004c10c0",
            "Evaluates simple-sprite expression tree recursively and returns scalar result (double).\n"
          + "Used by particle/simple-sprite runtime math dispatch."
        );
        updated++;

        setFnComment(
            "0x0044c440",
            "Rebuilds fear-grid occupancy state and schedules next update/tick flow.\n"
          + "Part of AI fear/avoidance runtime refresh path."
        );
        updated++;

        setFnComment(
            "0x004780f0",
            "Invokes world vtable slot +0x14 using temporary local buffers and returns callee result.\n"
          + "Call contract inferred from stack-local setup and virtual dispatch."
        );
        updated++;

        setFnComment(
            "0x00440ad0",
            "Builds grid index buffer (two triangles per cell) and optionally flips winding order.\n"
          + "Used by water render grid tessellation path."
        );
        updated++;

        setFnComment(
            "0x0055f44b",
            "Generic binary search over strided items using callback predicate.\n"
          + "Returns matched item offset/index token or 0 when not found."
        );
        updated++;

        setFnComment(
            "0x004d6e00",
            "Checks whether candidate unit is compatible for repair-pad docking based on bounds/slot thresholds and state gates."
        );
        updated++;

        setFnComment(
            "0x0044d560",
            "Advances frontend fade state machine and updates alpha byte at +0x18 using time-scaled interpolation."
        );
        updated++;

        setFnComment(
            "0x004f0ba0",
            "Computes tentacle world anchor from local basis/offset fields and writes result vector to caller output buffer."
        );
        updated++;

        println("ApplyWave217CommentPass1: updated=" + updated);
    }
}
