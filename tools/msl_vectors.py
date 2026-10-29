#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Writes companion/OnslaughtToolkit.Godot/Tests/ScriptVectors.g.cs: authored mission scripts and what the Toolkit's reference compiler
(tools/msl_compile.py) makes of each, for the C# compiler's tests to hold it to. Every vector is a source written for this purpose (none is
a game script) with the compile session's counters, the headers it includes and the names a missing header would have defined; the file
holds, for each, the compiled record as lines (the instructions, the entry points, the symbols, the named handlers, the two trailing words),
the notes the reference gave, or the message it refused with. The C# compiler must give the same lines, the same notes and the same
message, word for word.

    python tools/msl_vectors.py --check     fail if the committed C# file is not what --write writes
    python tools/msl_vectors.py --write     rewrite the C# file

The file also holds the reference's repr of some texts (the messages quote tokens with Python's repr) and its answer to every pair of
operators for `Compiler.binds_tighter`.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import msl_compile as mc  # noqa: E402

OUTPUT = ROOT / "companion/OnslaughtToolkit.Godot/Tests/ScriptVectors.g.cs"

VARS = "vars\n\tint a;\n\tint r;\nend_vars\ninit()\n{\n%s\n}\n"
BOOLS = "vars\n\tbool a;\n\tbool b;\n\tbool c;\n\tbool d;\n\tbool r;\nend_vars\ninit()\n{\n\t%s\n}\n"


def vector(name: str, why: str, source: str, includes: dict | None = None, const_start: int = 0, do_once_start: int = 0, resolve: dict | None = None) -> dict:
    return {"name": name, "why": why, "source": source, "includes": includes or {}, "constStart": const_start, "doOnceStart": do_once_start, "resolve": resolve or {}}


def nested(open_text: str, close_text: str, count: int, middle: str = "") -> str:
    return VARS % ("\t" + open_text * count + middle + close_text * count)


def deepest(make, limit: int = 400) -> int:
    """The largest depth for which make(depth) compiles, found by trying: the vectors sit on both sides of the reference's limit."""
    best = 0
    for count in range(1, limit):
        if "error" in compile_vector(vector("probe", "", make(count))):
            return best
        best = count
    return best


def vectors() -> list[dict]:
    v: list[dict] = []
    add = v.append

    # ---- the shapes the shipped scripts show
    add(vector("vars-and-a-call", "a vars block ends in a return; a call statement drops its result; the init entry point follows the block",
               "vars\n\tthing player;\nend_vars\ninit()\n{\n\tPause(1);\n}\n"))
    add(vector("no-vars", "a script without a vars block has a zero trailing word and no initialiser block", "init()\n{\n\tDie();\n}\n"))
    add(vector("vars-initialisers", "an initial value is a push and a pop; floats are float32", "vars\n\tint n = 4;\n\tfloat f = 1.5;\nend_vars\n"))
    add(vector("attributes-block", "the older keyword compiles the same as vars", "attributes\n\tint n = 4;\n\tfloat f = 1.5;\nend_attributes\n"))
    add(vector("empty-vars", "an empty vars block still ends in a return and sets the trailing word", "vars\nend_vars\n"))
    add(vector("call-result-use", "a call that is a whole statement has bit 16 clear; any other use of a call keeps it",
               "vars\n\tthing t;\nend_vars\ninit()\n{\n\tt = GetThingRef(\"x\");\n\tAttack(GetThingRef(\"y\"));\n\tif (GetHealth() < 5)\n\t{\n\t}\n}\n"))
    add(vector("member-calls", "a member call pushes its target, a pointer, then its own arguments",
               "vars\n\tthing u;\nend_vars\ninit()\n{\n\tu.Die();\n\tGetComponent(3).Shutdown();\n\tu.IsA(2);\n}\n"))
    add(vector("nested-calls", "an argument that is a call has its result used", "init()\n{\n\tRand(Rand(1));\n}\n"))
    add(vector("assignment-is-an-expression", "the value stays on the stack: a condition may assign",
               "vars\n\tbool v;\nend_vars\ninit()\n{\n\tif (v = TRUE)\n\t{\n\t}\n\tv = FALSE;\n}\n"))
    add(vector("chained-assignment", "an assignment's value can be assigned again", "vars\n\tint a;\n\tint b;\nend_vars\ninit()\n{\n\ta = b = 3;\n}\n"))
    add(vector("if-else-ladder", "if, else if, else: each branch jumps over the rest",
               "init()\n{\n\tif (GetHealth() < 5)\n\t{\n\t\tDie();\n\t}\n\telse if (GetHealth() < 9)\n\t{\n\t\tShutdown();\n\t}\n\telse\n\t{\n\t\tActivate();\n\t}\n}\n"))
    add(vector("if-without-braces", "a statement may stand in place of a block", "init()\n{\n\tif (GetHealth() < 5)\n\t\tDie();\n\telse\n\t\tActivate();\n}\n"))
    add(vector("while-loop", "the jump back goes to the condition", "init()\n{\n\twhile (GetHealth() > 1)\n\t{\n\t\tPause(1);\n\t}\n}\n"))
    add(vector("for-loop", "the step is read before the body, so its constants are numbered first, and runs after it",
               "vars\n\tint n;\nend_vars\ninit()\n{\n\tfor (n = 0; n < 3; n = n + 1)\n\t{\n\t\tPause(2);\n\t}\n}\n"))
    for index, header in enumerate(("for (; n < 3; n = n + 1)", "for (n = 0; ; n = n + 1)", "for (n = 0; n < 3; )")):
        add(vector(f"for-missing-part-{index}", "a for loop needs all three parts",
                   "vars\n\tint n;\nend_vars\ninit()\n{\n\t" + header + "\n\t{\n\t}\n}\n"))
    add(vector("switch-cases", "each case compares and drops the value; the end drops the switch value",
               "vars\n\tint n;\nend_vars\ninit()\n{\n\tswitch (n)\n\t{\n\t\tcase 1:\n\t\t{\n\t\t\tDie();\n\t\t}\n\t\tcase 2:\n\t\t{\n\t\t\tShutdown();\n\t\t}\n\t}\n}\n"))
    add(vector("do-once-twice", "a do_once block clears a flag; its two flag symbols come after every other symbol, numbered from the session's counter",
               "init()\n{\n\tdo_once\n\t{\n\t\tDie();\n\t}\n\tdo_once\n\t{\n\t\tShutdown();\n\t}\n}\n", do_once_start=5))
    add(vector("do-once-nested", "a do_once inside a do_once and in an event handler",
               "init()\n{\n\tdo_once\n\t{\n\t\tdo_once\n\t\t{\n\t\t\tDie();\n\t\t}\n\t}\n}\nevent(\"go\")\n{\n\tdo_once\n\t\tShutdown();\n}\n"))
    add(vector("event-handlers", "an event handler guards its body and names the first equal string constant",
               "init()\n{\n\tPostEvent(\"go\");\n}\nevent(\"go\")\n{\n\tDie();\n}\nevent(\"stop\")\n{\n\tDie();\n}\n"))
    add(vector("event-name-used-twice", "the handler's parameter is the first string constant of its name, here the earlier one",
               "event(\"go\")\n{\n\tPostEvent(\"go\");\n}\nevent(\"go\")\n{\n}\n"))
    add(vector("hit-and-a-misnamed-handler", "a handler with a parameter pops it; one named otherwise is compiled and never entered (a note says so)",
               "vars\n\tthing other;\nend_vars\nhit(other)\n{\n\tDie();\n}\ndies()\n{\n\tDie();\n}\n"))
    add(vector("every-fixed-event", "each of the first eight names is an entry point",
               "init()\n{\n}\narrived()\n{\n}\ntimer()\n{\n}\ndied()\n{\n}\nhit()\n{\n}\nstarted_dying()\n{\n}\nready()\n{\n}\nshutdown()\n{\n}\n"))
    add(vector("notdefined-names", "the names the game's table gives to its last five events are entry points too", "notdefined4()\n{\n}\nnotdefined8()\n{\n}\n"))
    add(vector("two-parameters", "a handler may name several variables", "vars\n\tthing a;\n\tthing b;\nend_vars\nhit(a, b)\n{\n}\n"))

    # ---- numbers and strings
    add(vector("numbers", "a number is one constant; -2.5 is a single negative constant; floats are float32; the f suffix is allowed",
               "init()\n{\n\tPause(-2.5);\n\tPause(0.24);\n\tPause(1.5f);\n\tRand(-7);\n\tSetVulnerable(FALSE);\n}\n"))
    add(vector("number-spellings", "digits with and without a point on either side, leading zeros, and the f suffix",
               "init()\n{\n\tPause(3.);\n\tPause(.5);\n\tPause(1.f);\n\tPause(007.50);\n\tRand(00000000000005);\n}\n"))
    add(vector("integer-limits", "the largest and smallest 32-bit integers", "init()\n{\n\tRand(2147483647);\n\tRand(-2147483648);\n}\n"))
    add(vector("float-limits", "the largest float32 and its negative",
               "init()\n{\n\tPause(340282346638528859811704183484516925440.0);\n\tPause(-340282346638528859811704183484516925440.0);\n}\n"))
    add(vector("integer-too-big", "2147483648 does not fit", "init()\n{\n\tRand(2147483648);\n}\n"))
    add(vector("negative-integer-too-big", "-2147483649 does not fit", "init()\n{\n\tRand(-2147483649);\n}\n"))
    add(vector("integer-eleven-digits", "an integer of more than ten digits does not fit, whatever its value", "init()\n{\n\tRand(99999999999);\n}\n"))
    add(vector("integer-fifteen-digits", "the message shows a long number cut short", "init()\n{\n\tRand(999999999999999);\n}\n"))
    add(vector("integer-with-many-digits", "the message does not repeat the whole number", "init()\n{\n\tRand(" + "9" * 400 + ");\n}\n"))
    add(vector("float-too-big", "a value that rounds past float32's largest is refused", "init()\n{\n\tPause(" + "9" * 39 + ".0);\n}\n"))
    add(vector("float-too-big-negative", "and so is its negative", "init()\n{\n\tPause(-" + "9" * 39 + ".0);\n}\n"))
    add(vector("string-with-a-quote", "a string may hold an apostrophe", "init()\n{\n\tPrint(\"it's\");\n}\n"))
    add(vector("string-not-single-byte", "a string holds single-byte characters only", "init()\n{\n\tPrint(\"\u2603\");\n}\n"))
    add(vector("string-first-past-latin-1", "U+0100 is the first character that is not a single byte", "init()\n{\n\tPrint(\"\u0100\");\n}\n"))
    add(vector("string-latin-1", "characters up to U+00FF are single bytes", "init()\n{\n\tPrint(\"caf\u00e9 \u00ff\");\n}\n"))
    add(vector("blanks-of-every-kind", "a tab, a carriage return, a form feed and a vertical tab are blanks", "init()\x0b\n{\x0c\r\n\tDie();\t\r\n}\r\n"))
    add(vector("comment-with-a-carriage-return", "a comment runs to the end of its line, a lone carriage return included", "init()\n{\n\tDie(); // a\rb c\n}\n"))
    add(vector("string-open-then-a-later-quote", "a string that does not close on its line is refused even if a quote follows on another line",
               "init()\n{\n\tPrint(\"a);\n\tPrint(\");\n}\n"))
    add(vector("bool-constants", "TRUE and FALSE are boolean constants", "init()\n{\n\tSetVulnerable(TRUE);\n\tSetVulnerable(FALSE);\n}\n"))

    # ---- grouping
    for index, text in enumerate(("r = a && b == c;", "r = a == b && c == d;", "r = a < b / 2;", "r = a - 1 <= b;", "r = a + 1 == b * 2;", "r = a != b;",
                                  "r = a + 1 != b;", "r = a != b != c;", "r = a || b || c;", "r = a - 1 - 2;", "r = a || (b && c);", "r = a + (b * 2);",
                                  "r = (a + b) * (c - d);", "r = a < b;", "r = a >= b;", "r = a > b;", "r = a * 2 * 3;")):
        add(vector(f"grouping-{index}", "operators that the shipped scripts settle, and parentheses", BOOLS % text))
    for index, (text, first, second) in enumerate((("a || b && c", "||", "&&"), ("a + b * 2", "+", "*"), ("a + b - 1", "+", "-"), ("a * 2 / b", "*", "/"),
                                                   ("a < b && c", "&&", "<"), ("a == b < c", "==", "<"), ("a != b && c", "!=", "&&"), ("a < b <= c", "<", "<="),
                                                   ("a && b || c", "&&", "||"), ("a + 1 && b", "&&", "+"))):
        add(vector(f"mixed-operators-{index}", f"{first} and {second} mixed without parentheses are refused naming both", BOOLS % f"r = {text};"))
    add(vector("grouping-note-in-a-condition", "a note says how a mixed chain was grouped, wherever the chain is",
               "vars\n\tbool a;\n\tbool b;\n\tbool c;\nend_vars\ninit()\n{\n\tif (a && b == c)\n\t{\n\t\tDie();\n\t}\n}\n"))
    add(vector("two-grouping-notes", "each chain with two operators or more gets its own note (the line and the spaced text)",
               "vars\n\tbool a;\n\tbool b;\n\tbool c;\nend_vars\ninit()\n{\n\tPause(1);\n\tif (a   &&\n\t\tb == c)\n\t{\n\t\tPause(2 + 3 - 4);\n\t}\n}\n"))

    # ---- refusals
    for index, (body, why) in enumerate((("Frobnicate(1);", "a function the game does not provide"), ("Pause();", "too few arguments"), ("Die(1);", "too many arguments"),
                                          ("m = 1;", "assignment to an undeclared name"), ("Pause(m);", "an undeclared name in an expression"),
                                          ("Pause(1)", "a missing semicolon"), ("Pause(\"open);", "a string that does not end on its line"),
                                          ("Pause(1); /* x */", "a block comment"), ("Pause(1) @;", "a character the language does not have"),
                                          ("n = ;", "an empty expression"), ("Pause(1 \"it's\");", "a string token in the message, with an apostrophe in it"),
                                          ("Pause(1 2);", "a number where a comma was expected"), ("Pause((1);", "a missing closing parenthesis"),
                                          ("else;", "a keyword used as a name"), ("n = 1 +;", "an operator with no right operand"),
                                          ("t.5;", "a member that is not a word"), ("Pause(12f);", "an f suffix on an integer is a word"),
                                          ("Pause(1\\);", "a backslash"), ("Pause(1) `;", "a backtick"), ("Pause(1) \\u00e9;", "a Latin-1 letter that is not a name"),
                                          ("Pause(1) \\u00a0;", "a no-break space is not a blank"), ("Pause(1) \\x01;", "a control character"),
                                          ("Pause(1) &;", "a single ampersand"), ("Pause(1) |;", "a single bar"),
                                          ("Pause(1) $;", "a dollar sign"), ("Pause(1)  /;", "a lone slash as a statement"))):
        text = body.replace("\\u00e9", "\u00e9").replace("\\u00a0", "\u00a0").replace("\\x01", "\x01")
        add(vector(f"refused-{index}", why, "vars\n\tint n;\n\tthing t;\nend_vars\ninit()\n{\n\t" + text + "\n}\n"))
    add(vector("handler-twice", "a fixed handler is written once", "init()\n{\n}\ninit()\n{\n}\n"))
    add(vector("unknown-type", "a type the language does not have", "vars\n\ttext s;\nend_vars\n"))
    add(vector("keyword-as-variable", "a variable cannot be named like a keyword", "vars\n\tint if;\nend_vars\n"))
    add(vector("event-name-not-a-string", "an event handler is named by a string", "event(go)\n{\n}\n"))
    add(vector("source-ends-in-a-block", "a block that never closes", "init()\n{\n\tDie();\n"))
    add(vector("source-ends-mid-statement", "a statement cut short", "init()\n{\n\tPause(1,"))
    add(vector("hit-with-a-non-variable", "a parameter that is not a declared variable", "hit(other)\n{\n}\n"))
    add(vector("a-keyword-as-a-handler", "a keyword where a handler belongs", "if (1) { }\n"))
    add(vector("while-as-a-handler", "a statement keyword where a handler belongs", "while()\n{\n}\n"))
    add(vector("variable-declared-twice", "a second declaration is the same symbol, with a note", "vars\n\tint n;\n\tfloat n;\nend_vars\n"))
    add(vector("error-on-the-fourth-line", "the message carries the line, counting from 1", "init()\n{\n\tDie();\n\tPause();\n}\n"))
    add(vector("expression-statement-of-a-name", "a variable alone is a statement that drops its value",
               "vars\n\tint a;\nend_vars\ninit()\n{\n\ta;\n}\n"))
    add(vector("empty-source", "an empty source compiles to an empty script", ""))
    add(vector("comments-only", "comments are dropped", "// nothing here\n// at all\n"))
    add(vector("a-block-statement", "braces nest statements", "init()\n{\n\t{\n\t\tDie();\n\t}\n}\n"))
    add(vector("unknown-type-note-free", "the declaration of a thing and a position", "vars\n\tthing t;\n\tposition p;\nend_vars\n"))

    # ---- headers, defines, counters, lines
    add(vector("symbol-lines", "symbol lines count newlines only; includes and defines leave their lines empty and a replaced name keeps the line of its use",
               "#include data\\a.msl\r\n#define LIMIT 3\nvars\r\n\tint n = LIMIT;\nend_vars\r\ninit()\r\n{\r\n\tPause(LIMIT);\n}\n", {"data/a.msl": "#define BASE 9\n"}))
    add(vector("include-in-any-case", "an include's path is matched in any case and with either slash; its defines are used",
               "#include DATA/Inc/Defs.MSL\ninit()\n{\n\tPause(TWICE);\n}\n", {"data/inc/defs.msl": "#define LIMIT 3\n#define TWICE LIMIT\n"}))
    add(vector("nested-includes", "a header's own #include lines are not followed (only its #define lines count)",
               "#include data\\a.msl\ninit()\n{\n\tPause(INNER);\n}\n", {"data/a.msl": "#include data\\b.msl\n#define OUTER 1\n", "data/b.msl": "#define INNER 2\n"}))
    add(vector("missing-include", "an include the game folder does not hold", "#include data\\nothing.msl\ninit()\n{\n}\n"))
    add(vector("define-with-a-comment", "a define's replacement stops at a comment", "#define FIVE 5 // five\ninit()\n{\n\tRand(FIVE);\n}\n"))
    add(vector("define-spacing", "blanks around the hash and after define; a define with no name is ignored",
               "  #  define   LOW 1\n\t#define\n#define HIGH   2   \ninit()\n{\n\tRand(LOW);\n\tRand(HIGH);\n}\n"))
    add(vector("define-of-a-word", "a define may stand for a name, a call or a whole statement part",
               "#define SAY Print(\"hi\")\n#define STOP Die()\ninit()\n{\n\tSAY;\n\tSTOP;\n}\n"))
    add(vector("define-names-itself", "a define that names itself stops expanding after sixteen levels and leaves the word", "#define LOOP LOOP\ninit()\n{\n\tPause(LOOP);\n}\n"))
    add(vector("define-chain", "a define of a define", "#define A B\n#define B C\n#define C 7\ninit()\n{\n\tRand(A);\n}\n"))
    chain16 = "".join(f"#define C{i} C{i + 1}\n" for i in range(15)) + "#define C15 7\n"  # C0 reaches 7 at the sixteenth replacement
    chain17 = "".join(f"#define C{i} C{i + 1}\n" for i in range(16)) + "#define C16 7\n"
    add(vector("define-chain-at-the-depth-limit", "sixteen replacements in a row are made", chain16 + "init()\n{\n\tRand(C0);\n}\n"))
    add(vector("define-chain-past-the-depth-limit", "the seventeenth is not: the name is left as a word", chain17 + "init()\n{\n\tRand(C0);\n}\n"))
    add(vector("define-with-slashes-in-a-string", "a // inside a string in a define is read as a comment, which cuts the string (the reference's reading)",
               "#define URL \"a//b\"\ninit()\n{\n\tPrint(URL);\n}\n"))
    add(vector("define-case-matters", "a define is found by its exact name", "#define limit 1\ninit()\n{\n\tRand(LIMIT);\n}\n"))
    add(vector("include-after-code", "a directive is a directive only at the start of its line", "init()\n{\n\tDie(); #include data\\a.msl\n}\n", {"data/a.msl": ""}))
    add(vector("define-redefined", "the last definition wins", "#define X 1\n#define X 2\ninit()\n{\n\tRand(X);\n}\n"))
    add(vector("define-not-in-a-string", "a name inside a string is not replaced", "#define WORD 9\ninit()\n{\n\tPrint(\"WORD\");\n}\n"))
    add(vector("define-keeps-the-use-line-in-notes", "a grouping note over replaced names reads the source text",
               "#define SAME a == b\nvars\n\tbool a;\n\tbool b;\n\tbool c;\nend_vars\ninit()\n{\n\tif (c && SAME)\n\t{\n\t}\n}\n"))
    add(vector("counters-from-the-session", "constants are numbered from the caller's counter", "init()\n{\n\tPause(1);\n\tPause(2);\n}\n", const_start=40))
    add(vector("do-once-counter", "do_once symbols are numbered from the caller's counter", "init()\n{\n\tdo_once\n\t{\n\t}\n}\n", do_once_start=12))
    add(vector("both-counters", "the two counters are independent", "init()\n{\n\tdo_once\n\t{\n\t\tPause(1);\n\t}\n}\n", const_start=7, do_once_start=3))
    add(vector("name-from-a-missing-header", "a name no header defines is refused unless the caller says what it stood for", "init()\n{\n\tPause(MYSTERY);\n}\n"))
    add(vector("name-given-by-the-caller", "the caller's constant is entered where the compiler needed one",
               "init()\n{\n\tPause(MYSTERY);\n}\n", resolve={"MYSTERY": ["int", 7]}))
    add(vector("names-given-by-the-caller", "several names, each with its own type and value",
               "init()\n{\n\tPause(HALF);\n\tPrint(GREETING);\n\tSetVulnerable(FLAG);\n}\n",
               resolve={"HALF": ["float", 0.5], "GREETING": ["string", "hello"], "FLAG": ["bool", 1]}))

    # ---- the limits
    limit = mc.MAX_DEPTH
    add(vector("blocks-at-the-limit", "nesting exactly at the reference's limit compiles", nested("{", "}", limit)))
    add(vector("blocks-past-the-limit", "one more is refused with the depth in the message", nested("{", "}", limit + 1)))
    add(vector("parentheses-past-the-limit", "so are nested parentheses", VARS % ("\tr = " + "(" * 300 + "a" + ")" * 300 + ";")))
    add(vector("calls-past-the-limit", "nested calls", VARS % ("\tr = " + "Rand(" * 300 + "1" + ")" * 300 + ";")))
    add(vector("assignments-past-the-limit", "chained assignments", VARS % ("\tr = " + "a = " * 300 + "a;")))
    paren_limit = deepest(lambda count: VARS % ("\tr = " + "(" * count + "a" + ")" * count + ";"))
    add(vector("parentheses-at-the-limit", "the deepest parentheses that compile", VARS % ("\tr = " + "(" * paren_limit + "a" + ")" * paren_limit + ";")))
    add(vector("parentheses-one-past", "and one more", VARS % ("\tr = " + "(" * (paren_limit + 1) + "a" + ")" * (paren_limit + 1) + ";")))
    add(vector("long-else-if-ladder", "a long ladder of branches is not nesting", VARS % ("\tif (a) { } " + "else if (a) { } " * 40)))
    add(vector("a-ladder-past-the-limit", "but each else if nests one deeper", VARS % ("\tif (a) { } " + "else if (a) { } " * 200)))
    add(vector("many-statements", "statements one after another do not add up to a depth", VARS % ("\tDie();\n" * 150)))

    # ---- a longer script
    add(vector("tutorial-shaped-script", "a script that uses most of the language together",
               "#define STEPS 3\nvars\n\tthing player;\n\tthing target;\n\tint count = 0;\n\tfloat delay = 0.5;\n\tbool done = FALSE;\nend_vars\n"
               "init()\n{\n\tPause(1.0);\n\tplayer = GetThingRef(\"Player\");\n\tfor (count = 0; count < STEPS; count = count + 1)\n\t{\n"
               "\t\tPostEvent(\"step\");\n\t\tPause(delay);\n\t}\n\tdo_once\n\t{\n\t\tPrint(\"ready\");\n\t}\n}\n"
               "event(\"step\")\n{\n\tif (count == STEPS && !done)\n\t{\n\t\tdone = TRUE;\n\t}\n\tswitch (count)\n\t{\n\t\tcase 1:\n\t\t{\n\t\t\tDie();\n\t\t}\n\t}\n}\n"
               "hit(target)\n{\n\ttarget.Die();\n}\n"))
    return v


def write_symbol(symbol: dict) -> str:
    value = symbol["value"]
    if value is None:
        shown = "-"
    elif symbol["dataType"] in (1, 4):
        shown = str(value)
    elif symbol["dataType"] == 2:
        shown = "f:" + struct.pack(">f", value).hex()  # the IEEE bits, most significant byte first
    elif symbol["dataType"] == 3:
        shown = "s:" + value.encode("latin-1").hex()
    else:
        raise AssertionError("an authored vector holds only the types a source can write")
    return f"symbol {symbol['index']} {symbol['name']} {symbol['dataType']} {shown} {symbol['symbolType']} {symbol['flag']}"


def dump(record: dict) -> list[str]:
    code = record["code"]
    assert record["trailer"] == mc.TRAILER, "the compiler writes the one trailer the shipped scripts have"
    lines = [f"name {record['name']}"]
    lines += [f"instruction {n} {mc.OPCODES[op]} {attr}" for n, (op, attr) in enumerate(code["instructions"])]
    lines += [f"eventPC {n} {pc}" for n, pc in enumerate(code["eventPCs"])]
    lines += [write_symbol(symbol) for symbol in code["symbols"]]
    lines.append(f"nextSymbolIndex {code['nextSymbolIndex']}")
    lines += [f"eventFunction {n} {f['entryPC']} {','.join(str(p) for p in f['params'])}" for n, f in enumerate(code["eventFunctions"])]
    lines.append(f"tail {code['tail'][0]} {code['tail'][1]}")
    return lines


def compile_vector(item: dict) -> dict:
    """What the reference makes of a vector: {"dump", "notes"} or {"error", "errorKind", "errorLine"}."""
    includes = item["includes"]

    def read(path: str) -> str:
        key = path.replace("\\", "/").lower()
        if key not in includes:
            raise mc.MissingInclude(path)
        return includes[key]

    table = item["resolve"]
    resolve = (lambda name, index: tuple(table[name]) if name in table else None) if table else None
    notes: list[mc.Note] = []
    try:
        record = mc.compile_script("t", item["source"], read, item["constStart"], item["doOnceStart"], resolve, notes)
    except mc.MissingInclude as error:
        return {"error": str(error), "errorKind": "missingInclude", "errorLine": -1, "errorPath": error.path}
    except mc.CompileError as error:
        return {"error": str(error), "errorKind": "error", "errorLine": -1 if error.line is None else error.line, "errorPath": ""}
    return {"dump": dump(record), "notes": [f"{note.line} {note.kind} {note.text}" for note in notes]}


REPR_TEXTS = ("", "plain", "it's", "say \"hi\"", "both ' and \"", "back\\slash", "tab\there", "line\nbreak", "cr\rhere", "\x01", "\x1f", "\x7f", "\x80", "\x9f",
              "\xa0", "\xad", "\u00e9", "\u00ff", "\u2603", "\u2028", "\U0001F600", "'", "\"", "\\", "a\u0301")

OPERATORS = ("||", "&&", "==", "!=", "<", "<=", ">", ">=", "+", "-", "*", "/")


def cs_text(text: str) -> str:
    out = ['"']
    for ch in text:
        code = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif code < 0x20 or code >= 0x7F:
            out.append(f"\\u{code:04x}" if code <= 0xFFFF else "".join(f"\\u{unit:04x}" for unit in struct.unpack("<2H", ch.encode("utf-16-le"))))
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def cs_array(items: list[str], indent: str) -> str:
    if not items:
        return "[]"
    return "[\n" + "".join(f"{indent}    {cs_text(item)},\n" for item in items) + f"{indent}]"


def render() -> str:
    out = [
        "// SPDX-License-Identifier: GPL-3.0-only",
        "// <auto-generated> by tools/msl_vectors.py from tools/msl_compile.py; do not edit it.",
        "// `python tools/msl_vectors.py --check` fails when this file is not what `--write` writes.",
        "#nullable enable",
        "namespace OnslaughtToolkit.Companion.Tests;",
        "",
        "/// <summary>An authored source and what the Toolkit's reference compiler makes of it: the compiled record as lines and its notes, or the message it refuses with.</summary>",
        "internal sealed record CompilerVector(string Name, string Why, string Source, (string Path, string Text)[] Includes, int ConstStart, int DoOnceStart,",
        "    (string Name, string Type, string Value)[] Resolve, string? Error, string ErrorKind, int ErrorLine, string ErrorPath, string[] Dump, string[] Notes);",
        "",
        "/// <summary>The reference's own answers for the C# compiler's tests (see tools/msl_vectors.py). Authored text only: no game script, no game bytes.</summary>",
        "internal static class ScriptVectors",
        "{",
        "    internal static readonly CompilerVector[] All =",
        "    [",
    ]
    for item in vectors():
        result = compile_vector(item)
        includes = ", ".join(f"({cs_text(path)}, {cs_text(text)})" for path, text in item["includes"].items())
        resolve = ", ".join(f"({cs_text(name)}, {cs_text(kind)}, {cs_text(str(value))})" for name, (kind, value) in item["resolve"].items())
        error = cs_text(result["error"]) if "error" in result else "null"
        out.append(f"        new({cs_text(item['name'])}, {cs_text(item['why'])}, {cs_text(item['source'])},")
        out.append(f"            [{includes}], {item['constStart']}, {item['doOnceStart']}, [{resolve}],")
        out.append(f"            {error}, {cs_text(result.get('errorKind', ''))}, {result.get('errorLine', -1)}, {cs_text(result.get('errorPath', ''))},")
        out.append(f"            {cs_array(result.get('dump', []), '            ')},")
        out.append(f"            {cs_array(result.get('notes', []), '            ')}),")
    out += ["    ];", "", "    /// <summary>Python's repr of each text, as the reference's messages quote a token.</summary>", "    internal static readonly (string Text, string Repr)[] Reprs ="]
    out.append("    [")
    out += [f"        ({cs_text(text)}, {cs_text(repr(text))})," for text in REPR_TEXTS]
    out += ["    ];", "", "    /// <summary>The reference's binds_tighter for each pair of operators (outer, inner): 1 the inner one is part of the right operand, 0 it ends it, -1 the shipped scripts do not say.</summary>",
            "    internal static readonly (string Outer, string Inner, int Answer)[] Grouping ="]
    out.append("    [")
    for outer in OPERATORS:
        for inner in OPERATORS:
            answer = mc.Compiler.binds_tighter(outer, inner)
            out.append(f"        ({cs_text(outer)}, {cs_text(inner)}, {-1 if answer is None else int(answer)}),")
    out += ["    ];", "}", ""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = render()
    if args.write:
        OUTPUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(text)} characters)")
        return 0
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text:
            print(f"FAIL {OUTPUT.relative_to(ROOT)} is not what `python tools/msl_vectors.py --write` writes")
            return 1
        print(f"{OUTPUT.relative_to(ROOT)} is current")
        return 0
    parser.error("choose --write or --check")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
