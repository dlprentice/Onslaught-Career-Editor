//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyOggMessageWave453 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedCurrentName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String expectedCurrentName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.expectedCurrentName = expectedCurrentName;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
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

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            Function containing = getFunctionContaining(entry);
            if (containing != null && containing.getEntryPoint().equals(entry)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
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
            "ogg-message-wave453",
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
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            String currentName = fn.getName();
            if (!currentName.equals(spec.expectedCurrentName) && !currentName.equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
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

            println("OK: " + spec.address + " " + readBack.getSignature());
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
        DataType byteType = ByteDataType.dataType;
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004b6cd0",
                "COggLoader__InitReadAndWaitThread",
                "COggLoader__readerSubobject_dtor_body",
                "__fastcall",
                voidType,
                "Wave453 name/signature/comment correction: reader-subobject destructor body reached by the COggLoader reader-subobject scalar-deleting destructor. Current instruction evidence adjusts through the reader-subobject path, invokes the current COggFileRead cleanup label, then invokes CWaitingThread cleanup; the old InitReadAndWaitThread label was stale. Static retail evidence only; exact COggLoader/COggFileRead layout, exact source identity, runtime streaming behavior, and rebuild parity remain unproven.",
                tags("ogg-loader", "destructor", "reader-subobject", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("reader_subobject", voidPtr)
                }
            ),
            new Spec(
                "0x004b6d30",
                "COggLoader__ctor_like_004b6d30",
                "COggLoader__ctor_base",
                "__fastcall",
                voidPtr,
                "Wave453 name/signature/comment correction: constructor/base initializer for the COggLoader waiting-thread plus Ogg-file reader object. Calls CWaitingThread construction on the base object, constructs the COggFileRead-style reader at +0x20, installs the base and reader-subobject vtables, and returns this. Static retail evidence only; exact class layout, source identity, runtime streaming behavior, and rebuild parity remain unproven.",
                tags("ogg-loader", "constructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b6d90",
                "COggLoader__VFunc_00_004b6d90",
                "COggLoader__ThreadProc_ReadPathIntoBuffer",
                "__fastcall",
                voidType,
                "Wave453 name/signature/comment correction: waiting-thread vfunc that checks the path byte at +0x102310, opens the Ogg reader subobject at +0x20, reads up to 0x100000 bytes into the buffer at +0x2310, stores the byte count/status at +0x102414, clears that count on read failure, and closes the reader on success. Static retail evidence only; exact buffer ownership, path semantics, runtime audio streaming behavior, and rebuild parity remain unproven.",
                tags("ogg-loader", "thread-proc", "audio", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b6df0",
                "COggLoader__VFunc_00_004b6df0",
                "COggLoader__readerSubobject_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave453 name/signature/comment correction: scalar-deleting destructor wrapper entered through the COggLoader reader-subobject vtable. Calls COggLoader__readerSubobject_dtor_body, conditionally frees the adjusted base pointer when flags bit 0 is set, returns that adjusted base pointer, and ret 0x4 confirms one stack flags argument. Static retail evidence only; exact subobject layout, source identity, runtime streaming behavior, and rebuild parity remain unproven.",
                tags("ogg-loader", "destructor", "scalar-deleting-dtor", "reader-subobject", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004b6e50",
                "CMessage__ctor_like_004b6e50",
                "CMessage__ctor_base",
                "__thiscall",
                voidPtr,
                "Wave453 name/signature/comment correction: constructor/base initializer for queued CMessage objects inserted by unit damage/effect and mission-script sound paths. Ret 0x1c confirms seven stack arguments after this; message_text is retained at +0x0c and measured with WcsLen, active_reader_target optionally initializes the active-reader cell at +0x30/+0x38, and queue_sort_key is stored at +0x2c for later MessageBox sorted insertion. Payload field semantics remain generic by design. Static retail evidence only; exact message layout, source identity, runtime dialog/audio behavior, and rebuild parity remain unproven.",
                tags("message", "constructor", "wide-text", "active-reader", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("payload0", intType),
                    param("message_text", shortPtr),
                    param("payload2", intType),
                    param("payload3", intType),
                    param("active_reader_target", voidPtr),
                    param("payload5", intType),
                    param("queue_sort_key", intType)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0 would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave453 apply had missing/bad entries");
        }
    }
}
