#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""A compiler for the mission script language (.msl), written from the decompilation's description of the script VM and its object-code
loader (cited by function, no source copied) and checked against the compiled scripts the game ships.

The game never reads .msl files: it runs the compiled scripts held in each level's world file (CWorld::LoadScripts 0x0050ac70 reads
each with CMissionScriptObjectCode's file constructor 0x00538ec0). The sources are the original compiler's input. This module turns a
source into the same record `world_resources_encode.read_world_model` gives for a compiled script (`name`, `code`, `trailer`), so a
compiled record can be compared field by field with the one the game shipped (`tools/msl_gate.py`) and written back into a world body.

A source is compiled to:
  instructions   the VM's instructions (opcode, attribute), as CAsmInstruction::Spawn (0x0052d3d0) reads them
  eventPCs       for each of the 13 fixed events the instruction where its handler starts, or -1
  symbols        the symbol table (CSymbolTable's file constructor 0x00539770): names, constants and variables in the order the compiler
                 met them, each with the 0-based line (counting \\n) where it first appeared. A name is entered once (the table's Find,
                 which CSymbolTable::Clone 0x005395b0 relies on); a constant is entered every time and is named `const dataN` from a
                 counter that belongs to the compile session, not to the script, so the caller says where it starts.
  eventFunctions the named handlers (CEventFunction's file constructor 0x0052fa70): an entry point and its event-name constant
  tail           two trailing words: 0, and 1 when the script has a vars block

What the shipped scripts show about the dialect, each verified against every shipped script it touches:
  - A call's attribute is native | argument count << 8, plus bit 16 when its result is used; a call that is a whole statement is
    followed by OP_REMOVE_TOP and has the bit clear.
  - An assignment is an expression: the value is pushed, OP_GETTOP copies it into the variable and leaves it, so `if (x = TRUE)` compiles.
    As a statement it is followed by OP_REMOVE_TOP.
  - `if`/`else`, `while`, `for` (the step is read before the body, so its constants are numbered first, and emitted after it), `switch`
    with `case` labels (no default), `do_once { }` (a flag the block clears; two boolean symbols `do-once-N` after every other symbol),
    handlers `init() died() started_dying() hit(var) ready() shutdown()` and `event("name")`. A handler named otherwise is compiled and
    never entered. A member call `target.Native(args)` pushes the target, OP_POINTER, then the arguments.
  - A vars ... end_vars block (one shipped script writes attributes ... end_attributes, which compiles the same) declares the script's variables:
    an initial value is OP_PUSH, OP_POP; the block ends in OP_RETURN even when empty; the declared types are not kept.
  - A number is one constant (`-2.0` is a single negative constant); floats are stored as float32; `TRUE` and `FALSE` are boolean constants.
  - Operator grouping is proven only in part (see `Compiler.binds_tighter`); everything else must be parenthesised.
"""
from __future__ import annotations

import errno
import math
import os
import re
import stat
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import world_resources_decode as wrd  # noqa: E402

OPCODES = wrd.OPCODES
OP = {name: index for index, name in enumerate(OPCODES)}
NATIVES = {name: index for index, (name, _types) in enumerate(wrd.SCRIPT_NATIVES)}
NATIVE_ARITY = {name: len(types) for name, types in wrd.SCRIPT_NATIVES}
# The 13 fixed events (SCRIPT_EVENT_NAMES, ScriptObjectCode.cpp 0x0064fef8): the names a script can give a handler of its own.
FIXED_EVENTS = wrd.SCRIPT_EVENT_NAMES
TRAILER = "656e645f736372697074"  # "end_script", as the world model shows bytes
USED = 1 << 16  # a CALL attribute's flag: the result is used (an argument, an assignment, a condition), not dropped
DT = {"int": 1, "float": 2, "string": 3, "bool": 4, "thing": 5, "position": 6}
DT_NAME = {value: name for name, value in DT.items()}
MAX_SOURCE = 1 << 20  # characters of a script, bytes of a header
MAX_TOKENS = 1 << 20  # tokens of a script after #define names are replaced
MAX_EXPANSION_STEPS = 4 << 20  # names looked at while replacing them (a define can expand to nothing, so tokens alone do not bound the work)
MAX_DEPTH = 100  # statements and expressions inside one another (the parser calls itself for each)
MAX_NOTE_CHARS = 5000  # characters of source text a grouping note may repeat (the expression once, each operand once more)
MAX_COUNTER = (1 << 31) - 1  # a compile-session counter (constants, do_once symbols) is numbered up to here, as the game stores an int
COUNTER_PAST = f"a counter of the compile session is past {MAX_COUNTER}"
KEYWORDS = frozenset({"if", "else", "while", "for", "switch", "case", "do_once", "vars", "end_vars", "attributes", "end_attributes"})


class CompileError(ValueError):
    def __init__(self, message: str, line: int | None = None):
        super().__init__(message if line is None else f"line {line + 1}: {message}")
        self.line = line


class MissingInclude(CompileError):
    """An #include names a file the game folder does not hold (a few shipped scripts name files that only the developers had)."""

    def __init__(self, path: str):
        super().__init__(f"the included file {path} is not in the game folder")
        self.path = path


@dataclass
class Note:
    """Something the compiler did that the author may want to see. `line` is 0-based."""
    line: int
    kind: str  # "grouping": how a mixed chain of operators was grouped; "handler": a handler the game never calls; "declaration"
    text: str


@dataclass
class Token:
    kind: str  # id, int, float, str, op
    text: str
    line: int  # 0-based, counting \n
    start: int = 0  # the token's span in the source text (a name from an #include or #define keeps the span of its use)
    end: int = 0


BLANK = r"[ \t\r\f\v]"  # what separates words on a source line: ASCII only, so that the C# compiler reads the same lines

TOKEN = re.compile(r"""
    (?P<ws>[ \t\r\f\v]+)
  | (?P<nl>\n)
  | (?P<comment>//[^\n]*)
  | (?P<float>(?:[0-9]+\.[0-9]*|\.[0-9]+)f?)
  | (?P<int>[0-9]+)
  | (?P<id>[A-Za-z_][A-Za-z_0-9]*)
  | (?P<str>"[^"\n]*")
  | (?P<op>==|!=|<=|>=|&&|\|\||[-+*/<>=!(){};,.:])
""", re.VERBOSE)


def lex(text: str) -> list[Token]:
    tokens, line, at = [], 0, 0
    while at < len(text):
        m = TOKEN.match(text, at)
        if not m:
            if text[at] == '"':
                raise CompileError("a string must end on the line it starts", line)
            raise CompileError(f"unexpected character {text[at]!r}", line)
        kind = m.lastgroup
        if kind == "nl":
            line += 1
        elif kind == "op" and m.group() == "/" and text.startswith("/*", at):
            raise CompileError("this language has no /* */ comments; use //", line)
        elif kind not in ("ws", "comment"):
            tokens.append(Token(kind, m.group(), line, at, m.end()))
        at = m.end()
    return tokens


def preprocess(source: str, read_include: Callable[[str], str]) -> tuple[list[Token], str]:
    """The source's tokens with its #include and #define lines applied, and the text they index. Lines count in the main source only."""
    defines: dict[str, list[Token]] = {}

    def define_from(text: str) -> None:
        for raw in text.split("\n"):
            m = re.match(rf"{BLANK}*#{BLANK}*define{BLANK}+([A-Za-z_][A-Za-z_0-9]*)(.*)$", raw)
            if m:
                defines[m.group(1)] = lex(re.sub(r"//.*", "", m.group(2)))

    def read_included(path: str) -> str:
        try:
            return read_include(path)
        except CompileError:
            raise
        except Exception:  # noqa: BLE001 - a reader that fails any other way is a header that cannot be read; no system text, so both compilers say the same
            raise CompileError(f"the included file {path} could not be read") from None

    body: list[str] = []
    for raw in source.split("\n"):
        m = re.match(rf"{BLANK}*#{BLANK}*include{BLANK}+([^ \t\r\f\v]+)", raw)
        if m:
            define_from(read_included(m.group(1)))
            body.append("")  # the line stays, so the lines after it keep their numbers
        elif re.match(rf"{BLANK}*#{BLANK}*define(?![A-Za-z0-9_])", raw):
            define_from(raw)
            body.append("")
        else:
            body.append(raw)
    text = "\n".join(body)
    out: list[Token] = []
    steps = [0]

    def expand(token: Token, use: Token, depth: int = 0) -> None:
        steps[0] += 1
        if steps[0] > MAX_EXPANSION_STEPS or len(out) >= MAX_TOKENS:
            raise CompileError(f"replacing the #define names makes the script longer than {MAX_TOKENS:,} tokens", use.line)
        if token.kind == "id" and token.text in defines and depth < 16:
            for inner in defines[token.text]:
                expand(inner, use, depth + 1)
        else:
            out.append(Token(token.kind, token.text, use.line, use.start, use.end))

    for token in lex(text):
        expand(token, token)
    return out, text


def spaced(text: str) -> str:
    """The text with each run of blanks and line ends one space (the same ASCII set the C# compiler uses)."""
    return " ".join(part for part in re.split(r"[ \t\n\r\f\v]+", text) if part)


class Chain:
    """What a chain of binary operators needs to write its grouping note: the operators it used, its operands (each the first and last
    token index of the operand) and the operators between them, and for each operand how many groups open before it and close after it.
    The grouping text is made from this only when a note is written, so reading a long chain costs the same per operator as a short one."""
    __slots__ = ("used", "leaves", "ops", "opens", "closes")

    def __init__(self) -> None:
        self.used: set[str] = set()
        self.leaves: list[tuple[int, int]] = []
        self.ops: list[str] = []
        self.opens: list[int] = []
        self.closes: list[int] = []


class Compiler:
    def __init__(self, name: str, tokens: list[Token], text: str, const_start: int, do_once_start: int = 0,
                 resolve: Callable | None = None, notes: list[Note] | None = None):
        self.name, self.t, self.text, self.i = name, tokens, text, 0
        self.do_once_next, self.do_once_sites, self.resolve, self.notes = do_once_start, [], resolve, notes
        self.variables: set[str] = set()
        self.handlers: set[str] = set()
        self.symbols: list[dict] = []
        self.symbol_index: dict[str, int] = {}  # the first symbol of each name (a name is entered once)
        self.string_index: dict[str, int] = {}  # the first string constant of each value (an event handler's parameter)
        self.code: list[tuple[int, int]] = []
        self.event_pcs = [-1] * 13
        self.event_functions: list[dict] = []
        self.const_next = const_start
        self.has_vars = False
        self.chains: list[Chain] = []
        self.depth = 0

    # ---- token helpers
    def peek(self, k: int = 0) -> Token | None:
        return self.t[self.i + k] if self.i + k < len(self.t) else None

    def next(self) -> Token:
        token = self.peek()
        if token is None:
            raise CompileError("the source ends in the middle of a statement")
        self.i += 1
        return token

    def accept(self, text: str) -> Token | None:
        token = self.peek()
        if token is not None and token.text == text and token.kind in ("id", "op"):
            self.i += 1
            return token
        return None

    def expect(self, text: str) -> Token:
        token = self.next()
        if token.text != text or token.kind not in ("id", "op"):
            raise CompileError(f"expected {text!r}, found {token.text!r}", token.line)
        return token

    def enter(self) -> None:
        """Called by each statement and expression before it reads on: the parser calls itself for every level of nesting, so the depth is bounded."""
        self.depth += 1
        if self.depth > MAX_DEPTH:
            token = self.peek()
            raise CompileError(f"statements and expressions are nested more than {MAX_DEPTH} deep", None if token is None else token.line)

    def note(self, line: int, kind: str, text: str) -> None:
        if self.notes is not None:
            self.notes.append(Note(line, kind, text))

    # ---- symbols and code
    def name_symbol(self, name: str, line: int) -> int:
        index = self.symbol_index.get(name)
        return index if index is not None else self.add(name, 0, None, line)

    def const(self, dtype: str, value, line: int) -> int:
        if self.const_next > MAX_COUNTER:
            raise CompileError(COUNTER_PAST, line)
        name = f"const data{self.const_next}"
        self.const_next += 1
        return self.add(name, DT[dtype], value, line)

    def add(self, name: str, dtype: int, value, line: int) -> int:
        index = len(self.symbols)
        self.symbols.append({"name": name, "dataType": dtype, "value": value, "symbolType": line, "index": index, "flag": 1})
        self.symbol_index.setdefault(name, index)
        if dtype == DT["string"] and isinstance(value, str):
            self.string_index.setdefault(value, index)
        return index

    def emit(self, op: str, attr: int = -1) -> int:
        self.code.append((OP[op], attr))
        return len(self.code) - 1

    def patch(self, jump: int) -> None:
        """Points the jump at the label that comes next."""
        self.code[jump] = (self.code[jump][0], len(self.code))

    # ---- the script
    def script(self) -> dict:
        if self.peek() is not None and self.peek().text in self.VARS_BLOCKS:
            self.vars_block()
        while self.peek() is not None:
            self.handler()
        self.add_do_once_symbols()
        code = {"instructions": self.code, "eventPCs": self.event_pcs, "symbols": self.symbols, "nextSymbolIndex": len(self.symbols),
                "eventFunctions": self.event_functions, "tail": [0, 1 if self.has_vars else 0]}
        return {"name": self.name, "code": code, "trailer": TRAILER}

    def add_do_once_symbols(self) -> None:
        """Each do_once block has two boolean symbols, a flag (true) and a false constant, after every other symbol of the script."""
        for flag_pc, zero_pc, set_pc, line in self.do_once_sites:
            if self.do_once_next + 1 > MAX_COUNTER:  # the block's two symbols are numbered N and N + 1
                raise CompileError(COUNTER_PAST, line)
            flag = self.add(f"do-once-{self.do_once_next}", DT["bool"], 1, 0)
            zero = self.add(f"do-once-{self.do_once_next + 1}", DT["bool"], 0, 0)
            self.do_once_next += 2
            self.code[flag_pc] = (OP["OP_PUSH"], flag)
            self.code[zero_pc] = (OP["OP_PUSH"], zero)
            self.code[set_pc] = (OP["OP_POP"], flag)

    VARS_BLOCKS = {"vars": "end_vars", "attributes": "end_attributes"}  # the older keyword compiles the same (one shipped script)

    def vars_block(self) -> None:
        closer = self.VARS_BLOCKS[self.next().text]
        self.has_vars = True
        while not self.accept(closer):
            type_token = self.next()
            if type_token.text not in DT:
                raise CompileError(f"unknown type {type_token.text!r}", type_token.line)
            name = self.next()
            if name.kind != "id" or name.text in KEYWORDS:
                raise CompileError(f"expected a variable name, found {name.text!r}", name.line)
            if name.text in self.variables:  # a shipped script declares one twice: the second is the same symbol
                self.note(name.line, "declaration", f"{name.text} is declared more than once; it is one variable")
            variable = self.name_symbol(name.text, name.line)
            self.variables.add(name.text)
            if self.accept("="):
                self.expression()
                self.emit("OP_POP", variable)
            self.expect(";")
        self.emit("OP_RETURN")

    def handler(self) -> None:
        token = self.next()
        if token.text == "event" and token.kind == "id":
            self.expect("(")
            name = self.next()
            if name.kind != "str":
                raise CompileError("an event handler is named by a string", name.line)
            value = self.string_value(name)
            self.const("string", value, name.line)
            # The handler's parameter is the first string constant of that value (the one just made unless the script used the text before).
            parameter = self.string_index[value]
            self.expect(")")
            self.event_functions.append({"entryPC": len(self.code), "params": [parameter]})
            end = self.emit("OP_JMPFALSE", 0)
            self.block()
            self.patch(end)
            self.emit("OP_LABEL")
            self.emit("OP_RETURN")
            return
        if token.kind != "id" or token.text in KEYWORDS:
            raise CompileError(f"expected an event handler such as init() or event(\"name\"), found {token.text!r}", token.line)
        if token.text in self.handlers:
            raise CompileError(f"the {token.text} handler is written twice", token.line)
        self.handlers.add(token.text)
        self.name_symbol(token.text, token.line)
        self.expect("(")
        parameters = []
        if not self.accept(")"):
            while True:
                parameters.append(self.next())
                if self.accept(")"):
                    break
                self.expect(",")
        if token.text in FIXED_EVENTS:
            self.event_pcs[FIXED_EVENTS.index(token.text)] = len(self.code)
        else:
            self.note(token.line, "handler", f"{token.text}() is not one of the game's events ({', '.join(FIXED_EVENTS[:8])}), "
                                             "so it is compiled and never called")
        for parameter in parameters:
            self.emit("OP_POP", self.variable(parameter))
        self.block()
        self.emit("OP_RETURN")

    def block(self) -> None:
        self.expect("{")
        while not self.accept("}"):
            self.statement()

    # ---- statements
    STATEMENTS = {"if": "if_statement", "while": "while_statement", "for": "for_statement", "switch": "switch_statement",
                  "do_once": "do_once_statement"}

    def statement(self) -> None:
        token = self.peek()
        if token is None:
            raise CompileError("the source ends inside a block")
        self.enter()
        try:
            if token.kind == "op" and token.text == "{":
                self.block()
            elif token.kind == "id" and token.text in self.STATEMENTS:
                getattr(self, self.STATEMENTS[token.text])()
            else:
                self.simple_statement()
                self.expect(";")
        finally:
            self.depth -= 1

    def simple_statement(self) -> None:
        """An expression whose value is dropped."""
        self.expression()
        if self.code and self.code[-1][0] == OP["OP_CALL"]:  # a call that is the whole statement: its result is dropped, not used
            self.code[-1] = (OP["OP_CALL"], self.code[-1][1] & 0xFFFF)
        self.emit("OP_REMOVE_TOP")

    def do_once_statement(self) -> None:
        """A block that runs the first time only: it clears a flag that it tests (the flag symbols are numbered when the script ends)."""
        do_once = self.expect("do_once")
        flag_pc = self.emit("OP_PUSH", -1)
        skip = self.emit("OP_JMPFALSE", 0)
        zero_pc = self.emit("OP_PUSH", -1)
        set_pc = self.emit("OP_POP", -1)
        self.do_once_sites.append((flag_pc, zero_pc, set_pc, do_once.line))
        self.statement()
        self.patch(skip)
        self.emit("OP_LABEL")

    def if_statement(self) -> None:
        self.expect("if")
        self.expect("(")
        self.expression()
        self.expect(")")
        skip = self.emit("OP_JMPFALSE", 0)
        self.statement()
        if self.accept("else"):
            over = self.emit("OP_JMP", 0)
            self.patch(skip)
            self.emit("OP_LABEL")
            self.statement()
            self.patch(over)
        else:
            self.patch(skip)
        self.emit("OP_LABEL")

    def while_statement(self) -> None:
        self.expect("while")
        top = len(self.code)
        self.expect("(")
        self.expression()
        self.expect(")")
        leave = self.emit("OP_JMPFALSE", 0)
        self.statement()
        self.emit("OP_JMP", top)
        self.patch(leave)
        self.emit("OP_LABEL")

    def for_statement(self) -> None:
        # All three parts are required: every shipped for loop has them, and what an empty one compiles to is not shown.
        for_token = self.expect("for")
        self.expect("(")
        if self.peek() is not None and self.peek().text in (";", ")"):
            raise CompileError("a for loop needs a first statement, a condition and a step", for_token.line)
        self.simple_statement()
        self.expect(";")
        top = len(self.code)
        if self.peek() is not None and self.peek().text in (";", ")"):
            raise CompileError("a for loop needs a first statement, a condition and a step", for_token.line)
        self.expression()
        self.expect(";")
        leave = self.emit("OP_JMPFALSE", 0)
        # The step is read before the body (its constants are numbered first) and runs after it.
        body_code, self.code = self.code, []
        if self.peek() is not None and self.peek().text == ")":
            raise CompileError("a for loop needs a first statement, a condition and a step", for_token.line)
        self.simple_statement()
        step, self.code = self.code, body_code
        self.expect(")")
        self.statement()
        self.code.extend(step)
        self.emit("OP_JMP", top)
        self.patch(leave)
        self.emit("OP_LABEL")

    def switch_statement(self) -> None:
        self.expect("switch")
        self.expect("(")
        self.expression()
        self.expect(")")
        self.expect("{")
        ends = []
        while not self.accept("}"):
            self.expect("case")
            self.expression()
            self.expect(":")
            self.emit("OP_CMP")
            self.emit("OP_REMOVE_TOP")
            next_case = self.emit("OP_JMPNE", 0)
            self.statement()
            ends.append(self.emit("OP_JMP", 0))
            self.patch(next_case)
            self.emit("OP_LABEL")
        for jump in ends:
            self.patch(jump)
        self.emit("OP_LABEL")
        self.emit("OP_REMOVE_TOP")

    # ---- expressions
    BINARY_OPS = {"||": "OP_OR", "&&": "OP_AND", "==": "OP_CMPB", "!=": "OP_CMPNEB", "<": "OP_LESS_THAN", "<=": "OP_LESS_EQ_THAN",
                  ">": "OP_GREAT_THAN", ">=": "OP_GREAT_EQ_THAN", "+": "OP_PLUS", "-": "OP_MINUS", "*": "OP_MULTIPLY", "/": "OP_DIVIDE"}
    ARITHMETIC = ("+", "-", "*", "/")
    COMPARISON = ("==", "!=", "<", "<=", ">", ">=")

    @classmethod
    def binds_tighter(cls, outer: str, inner: str) -> bool | None:
        """Whether `inner`, met while reading the right operand of `outer`, is part of that operand (True) or ends it (False), or None
        when the shipped scripts do not say. What they prove: repeating one operator groups left to right; `&&` and `==` have one rank
        and group left to right (`a && b == c` is `(a && b) == c`, unlike C); + - * / bind tighter than the comparisons. Every shipped
        script puts parentheses around anything else, so the grouping the original compiler gave it is unknown."""
        if outer == inner or {outer, inner} == {"&&", "=="}:
            return False
        if outer in cls.COMPARISON and inner in cls.ARITHMETIC:
            return True
        if outer in cls.ARITHMETIC and inner in cls.COMPARISON:
            return False
        return None

    def expression(self) -> None:
        """An assignment (its value stays on the stack) or a chain of binary operators. A chain that mixes operators gets a note."""
        token, nxt = self.peek(), self.peek(1)
        self.enter()
        try:
            if token is not None and token.kind == "id" and nxt is not None and nxt.kind == "op" and nxt.text == "=":
                variable = self.variable(token)
                self.i += 2
                self.expression()
                self.emit("OP_GETTOP", variable)
                return
            chain = Chain()
            self.chains.append(chain)
            first = self.i
            self.binary(None)
            self.chains.pop()
            if len(chain.used) >= 2:
                self.note(self.t[first].line, "grouping", self.grouping_note(chain, self.t[first], self.t[self.i - 1]))
        finally:
            self.depth -= 1

    def grouping_note(self, chain: Chain, first: Token, last: Token) -> str:
        """How a mixed chain was grouped: its text as written (blanks as one space) and the same text with each group in parentheses.
        The note repeats the chain's text once whole and once for each operand, so a chain whose text adds up to more than MAX_NOTE_CHARS
        characters (counted as written, before blanks are folded) gets a fixed sentence in its place."""
        size = max(0, last.end - first.start) + sum(max(0, self.t[b].end - self.t[a].start) for a, b in chain.leaves)
        if size > MAX_NOTE_CHARS:
            return f"the grouping of this expression is not written out: its text is longer than {MAX_NOTE_CHARS} characters"
        parts = []
        for k, (a, b) in enumerate(chain.leaves):
            parts.append("(" * chain.opens[k] + spaced(self.span(self.t[a], self.t[b])) + ")" * chain.closes[k])
            if k < len(chain.ops):
                parts.append(f" {chain.ops[k]} ")
        return f"{spaced(self.span(first, last))} is grouped {''.join(parts)}"

    def span(self, first: Token, last: Token) -> str:
        return self.text[first.start:last.end]

    def variable(self, token: Token) -> int:
        if token.kind != "id" or token.text not in self.variables:
            raise CompileError(f"{token.text!r} is not a variable of this script", token.line)
        return self.name_symbol(token.text, token.line)

    def binary(self, outer: str | None) -> tuple[int, int]:
        """A chain of binary operators read left to right; returns the first and last operand (by number in the chain) of the group read."""
        left = self.operand()
        while True:
            token = self.peek()
            if token is None or token.kind != "op" or token.text not in self.BINARY_OPS:
                return left
            if outer is not None:
                tighter = self.binds_tighter(outer, token.text)
                if tighter is None:
                    raise CompileError(f"{outer!r} and {token.text!r} are mixed without parentheses: the shipped scripts never leave "
                                       "their grouping to the game's compiler, so put parentheses around the part you mean first",
                                       token.line)
                if not tighter:
                    return left
            self.i += 1
            chain = self.chains[-1]
            chain.used.add(token.text)
            chain.ops.append(token.text)
            right = self.binary(token.text)
            self.emit(self.BINARY_OPS[token.text])
            chain.opens[left[0]] += 1  # (left op right) is one more group, round everything from left's first operand to right's last
            chain.closes[right[1]] += 1
            left = (left[0], right[1])

    def operand(self) -> tuple[int, int]:
        first = self.i
        token = self.next()
        if token.kind == "op" and token.text == "(":
            self.expression()
            self.expect(")")
        elif token.kind == "str":
            self.emit("OP_PUSH", self.const("string", self.string_value(token), token.line))
        elif token.kind in ("int", "float"):
            self.number(token, 1)
        elif token.kind == "op" and token.text == "-" and self.peek() is not None and self.peek().kind in ("int", "float"):
            self.number(self.next(), -1)
        elif token.kind == "id" and token.text in ("TRUE", "FALSE"):
            self.emit("OP_PUSH", self.const("bool", 1 if token.text == "TRUE" else 0, token.line))
        elif token.kind == "id" and self.peek() is not None and self.peek().text == "(" and self.peek().kind == "op":
            self.call(token)
        elif token.kind == "id" and token.text in KEYWORDS:
            raise CompileError(f"{token.text!r} is a keyword and cannot be used here", token.line)
        elif token.kind == "id" and token.text in self.variables:
            self.emit("OP_PUSH", self.name_symbol(token.text, token.line))
        elif token.kind == "id":
            # Not a variable: a name an included file should have defined. When that file is missing the caller may say what it stood for.
            value = self.resolve(token.text, len(self.symbols)) if self.resolve else None
            if value is None:
                raise CompileError(f"{token.text!r} is neither a variable of this script nor a name an included file defines", token.line)
            self.emit("OP_PUSH", self.const(*value, token.line))
        else:
            raise CompileError(f"cannot compile an expression starting {token.text!r}", token.line)
        while self.accept("."):
            member = self.next()
            if member.kind != "id":
                raise CompileError("a member is named by a word", member.line)
            self.emit("OP_POINTER")
            self.call(member)
        chain = self.chains[-1]
        chain.leaves.append((first, self.i - 1))
        chain.opens.append(0)
        chain.closes.append(0)
        return len(chain.leaves) - 1, len(chain.leaves) - 1

    def string_value(self, token: Token) -> str:
        value = token.text[1:-1]
        try:
            value.encode("latin-1")
        except UnicodeEncodeError:
            raise CompileError("a string holds single-byte characters only", token.line) from None
        return value

    def number(self, token: Token, sign: int) -> None:
        shown = token.text if len(token.text) <= 14 else token.text[:12] + "..."
        if token.kind == "int":
            digits = token.text.lstrip("0") or "0"
            if len(digits) > 10:  # more than any 32-bit number has (and it keeps int() clear of Python's limit on digits)
                raise CompileError(f"{shown} does not fit in 32 bits", token.line)
            value = sign * int(digits)
            if not -(1 << 31) <= value < (1 << 31):
                raise CompileError(f"{sign * int(digits)} does not fit in 32 bits", token.line)
            self.emit("OP_PUSH", self.const("int", value, token.line))
        else:
            wide = sign * float(token.text.rstrip("f"))
            try:
                if not math.isfinite(wide):
                    raise OverflowError
                value = struct.unpack("<f", struct.pack("<f", wide))[0]
            except OverflowError:
                raise CompileError(f"{shown} is too large for a float", token.line) from None
            self.emit("OP_PUSH", self.const("float", value, token.line))

    def call(self, name: Token) -> None:
        """A call whose name has been read: its name is entered, then its arguments are read left to right."""
        if name.text not in NATIVES:
            raise CompileError(f"{name.text!r} is not a function the game provides", name.line)
        self.name_symbol(name.text, name.line)
        self.expect("(")
        n = 0
        if not self.accept(")"):
            while True:
                self.expression()
                n += 1
                if self.accept(")"):
                    break
                self.expect(",")
        if n != NATIVE_ARITY[name.text]:
            raise CompileError(f"{name.text} takes {NATIVE_ARITY[name.text]} argument(s), not {n}", name.line)
        self.emit("OP_CALL", NATIVES[name.text] | (n << 8) | USED)


def compile_script(name: str, source: str, read_include: Callable[[str], str], const_start: int = 0, do_once_start: int = 0,
                   resolve: Callable | None = None, notes: list[Note] | None = None) -> dict:
    """The compiled record of one script's source (see the module docstring). `const_start` numbers its first constant and
    `do_once_start` its first do_once symbol (both counters belong to the compile session, not to the script); `resolve(name, index)` may
    give (type, value) for a name a missing include would have defined; `notes` collects what the author may want to see."""
    if len(source) > MAX_SOURCE:
        raise CompileError("the script is longer than a million characters")
    tokens, text = preprocess(source, read_include)
    return Compiler(name, tokens, text, const_start, do_once_start, resolve, notes).script()


NO_GAME_FOLDER = "no game folder is given"
ASCII_LOWER = {code: code + 32 for code in range(ord("A"), ord("Z") + 1)}  # names match in any ASCII letter case, and in no other (the C# compiler does the same)


def link_message(shown: str) -> str:
    return f"{shown} is a link or goes through one, which is not followed"


def is_link(info: os.stat_result) -> bool:
    """A symbolic link or, on Windows, any other reparse point (a junction, ...)."""
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def entry_named(folder: str, name: str) -> tuple[str, bool] | None:
    """The entry of `folder` called `name` in any ASCII letter case, with whether it is a link: the exact spelling if the folder has it,
    else the smallest spelling in code order (so two entries that differ only in case are never chosen by the order the folder lists)."""
    wanted = name.translate(ASCII_LOWER)
    found: dict[str, bool] = {}
    with os.scandir(folder) as entries:
        for entry in entries:
            if entry.name.translate(ASCII_LOWER) == wanted:
                found[entry.name] = is_link(entry.stat(follow_symlinks=False)) if os.name == "nt" else entry.is_symlink()
    if not found:
        return None
    chosen = name if name in found else min(found)
    return chosen, found[chosen]


def game_file(game_root: Path | str | None, path: str) -> Path:
    """The file a game-relative path names (backslashes, any ASCII letter case: the game's files are named for Windows), kept inside the
    game folder. Nothing on the way below the game folder, and not the file itself, may be a link: a link is not followed, so what the
    lookup checked is what is read. The game folder itself may be reached through links. A reader that fails is a CompileError, never an
    OSError: the message carries no system text."""
    if game_root is None or os.fspath(game_root) in ("", b""):
        raise CompileError(NO_GAME_FOLDER)
    unreadable = CompileError(f"the included file {path} could not be read")
    try:
        root = os.fsdecode(os.fspath(game_root))
        if "\x00" in root:
            raise unreadable
        at = os.path.abspath(root)
        for part in path.replace("\\", "/").split("/"):
            if not part or part == ".":
                continue
            if part == "..":
                raise CompileError(f"a path cannot climb out of the game folder: {path}")
            found = entry_named(at, part) if os.path.isdir(at) else None
            if found is None:
                raise MissingInclude(path)
            if found[1]:
                raise CompileError(link_message(path))
            at = os.path.join(at, found[0])
        regular = stat.S_ISREG(os.lstat(at).st_mode)
    except CompileError:
        raise
    except Exception:  # noqa: BLE001 - a permission, a folder that cannot be listed, a name the system rejects: all "could not be read"
        raise unreadable from None
    if not regular:
        raise CompileError(f"{path} is not a file inside the game folder")
    return Path(at)


def read_file(path: str, limit: int) -> tuple[str | None, bytes]:
    """(problem, bytes) for the file at `path`, opened once and never followed: the file is opened without blocking and without following
    a link, and its type and size are those of the open file, so nothing swapped in after a look can make the read wait (a named pipe
    would wait for a writer for ever) or pass the size limit. The problem is None, "link", "not a file", "too long" or "unreadable"."""
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        if not hasattr(os, "O_NOFOLLOW") and is_link(os.lstat(path)):  # no such flag (Windows): look first
            return "link", b""
        fd = os.open(path, flags)
    except OSError as error:
        return ("link" if error.errno == errno.ELOOP else "unreadable"), b""
    except ValueError:  # an embedded null character
        return "unreadable", b""
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            return "not a file", b""
        if info.st_size > limit:
            return "too long", b""
        chunks, total = [], 0
        while total <= limit:  # a file that grows while it is read is cut at the limit and refused
            chunk = os.read(fd, min(1 << 16, limit + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        return ("too long", b"") if total > limit else (None, b"".join(chunks))
    except OSError:
        return "unreadable", b""
    finally:
        os.close(fd)


def read_source(path: Path | str, included_as: str | None = None) -> str:
    """A script or header as text: the game's files are single-byte text. `included_as` is the include path as written, when the file is
    a header (the messages then name it); the file must not be a link, must be a regular file and may hold a million bytes."""
    file = os.fspath(path)
    shown = included_as if included_as is not None else os.path.basename(file)
    problem, data = read_file(file, MAX_SOURCE)
    if problem == "link":
        raise CompileError(link_message(shown))
    if problem == "not a file":
        raise CompileError(f"{shown} is not a file inside the game folder")
    if problem == "too long":
        raise CompileError(f"{os.path.basename(file)} is longer than a million bytes")
    if problem == "unreadable":
        raise CompileError(f"the included file {shown} could not be read" if included_as is not None else f"{shown} could not be read")
    return data.decode("latin-1")


def includes_from(game_root: Path | str | None) -> Callable[[str], str]:
    """Reads an included file by the game-relative path the source names."""
    return lambda path: read_source(game_file(game_root, path), included_as=path)


def counter_start(record: dict, pattern: str) -> int:
    for symbol in record["code"]["symbols"]:
        m = re.fullmatch(pattern, symbol["name"])
        if m:
            digits = m.group(1).lstrip("0")  # a long run of digits is refused before it is made a number
            if len(digits) > 10 or int(digits or "0") > MAX_COUNTER:
                raise CompileError(COUNTER_PAST)
            return int(digits or "0")
    return 0


def const_start_of(record: dict) -> int:
    """The number of the first constant of a shipped script (the counter is the compile session's, the source cannot give it), or 0."""
    return counter_start(record, r"const data([0-9]+)")


def do_once_start_of(record: dict) -> int:
    """The number of the first do_once symbol of a shipped script, or 0."""
    return counter_start(record, r"do-once-([0-9]+)")


def normal(record: dict) -> dict:
    """A record in one comparable form (lists, not tuples)."""
    code = record["code"]
    return {"name": record["name"], "trailer": record["trailer"], "code": {
        "instructions": [list(i) for i in code["instructions"]], "eventPCs": list(code["eventPCs"]),
        "symbols": [dict(s) for s in code["symbols"]], "nextSymbolIndex": code["nextSymbolIndex"],
        "eventFunctions": [{"entryPC": f["entryPC"], "params": list(f["params"])} for f in code["eventFunctions"]], "tail": list(code["tail"])}}


def first_difference(compiled: dict, shipped: dict) -> str | None:
    """None when the two records are the same, else the first field that differs, with both values."""
    a, b = normal(compiled), normal(shipped)
    if a == b:
        return None
    for key in ("name", "trailer"):
        if a[key] != b[key]:
            return f"{key}: {a[key]!r} against {b[key]!r}"
    ca, cb = a["code"], b["code"]
    for key in ("instructions", "eventPCs", "symbols", "nextSymbolIndex", "eventFunctions", "tail"):
        if ca[key] != cb[key]:
            if isinstance(ca[key], list) and len(ca[key]) and len(cb[key]):
                for n, (x, y) in enumerate(zip(ca[key], cb[key])):
                    if x != y:
                        return f"{key}[{n}]: {x!r} against {y!r}"
                return f"{key}: {len(ca[key])} entries against {len(cb[key])}"
            return f"{key}: {ca[key]!r} against {cb[key]!r}"
    return "different"


if __name__ == "__main__":
    raise SystemExit("usage: this module is used by tools/msl_gate.py and tools/msl_compile_tests.py")
