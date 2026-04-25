# Mini-C to RISC-V Compiler

A compiler that translates Mini-C source code into RISC-V assembly, implemented in Python using ANTLR4 for lexing and parsing, and custom AST visitors for semantic analysis and code generation.

---

## Table of Contents

1. [Compiler Phases](#compiler-phases)
2. [Memory Model & Register Use](#memory-model--register-use)
3. [Calling Conventions](#calling-conventions)
4. [Reflection](#reflection)

---

## Compiler Phases

The compiler consists of four phases, each transforming or validating the input through different intermediate representations (IRs). The first two phases leverage ANTLR4-generated code, while the latter two implement custom visitors over an Abstract Syntax Tree (AST) produced from the parse tree.

### Phase 1: Lexical Analysis

- **Implementation:** ANTLR4-generated `MiniLexer` from `Mini.g4` grammar
- **Input:** Raw source code (`.mini` file)
- **Output:** Token stream IR (keywords, identifiers, literals, operators)

In a single pass, the lexer transforms a character stream into categorized tokens using regular expression rules defined in `Mini.g4`.

---

### Phase 2: Syntax Analysis

- **Implementation:** ANTLR4-generated `MiniParser` from `Mini.g4` grammar
- **Input:** Token stream IR from lexer
- **Output:** Parse Tree IR with context objects (e.g. `ProgramContext`, `TypesContext`, `StructTypeContext`)

In a single pass, the parser validates grammatical correctness according to the Mini-C grammar. Syntax errors are detected at this phase.

---

### Phase 3a: AST Construction

- **Implementation:** Custom `MiniToASTVisitor` in `mini_ast_visitor.py`
- **Input:** Parse Tree IR
- **Output:** AST

Transforms the parse tree into a more compact and semantically meaningful AST for use in subsequent phases.

---

### Phase 3b: Semantic Analysis

- **Implementation:** Custom `SSASTVisitor` in `static_semantic_ast_visitor.py`
- **Input:** AST
- **Output:** Validated AST

Performs semantic validation including:

- **Scope checking** — maintains `global_scope`, `struct_scope`, `function_scope`, and `current_scope` symbol tables to detect undeclared variables, duplicate declarations, and scope violations (e.g. structs declared before their definition)
- **Type checking** — validates type compatibility for assignments, binary/unary operations, function calls, and return statements

Errors are accumulated in `total_errors` and reported. If any errors are found, compilation halts before code generation.

---

### Phase 4: Code Generation

- **Implementation:** Custom `ISASTVisitor` in `instruction_selection_ast_visitor.py`
- **Input:** Validated AST
- **Output:** RISC-V assembly code

Generates RISC-V assembly using the symbol table dictionaries from `SSASTVisitor`. Key responsibilities include frame management, struct layout, calling conventions, expression evaluation, and statement translation.

---

## Memory Model & Register Use

The compiler uses a **memory-to-memory model** — values are primarily stored in memory (stack, data segment, or heap) and temporarily loaded into registers for computation.

### Stack Frame Layout

Each function frame is precomputed at program start by `generate_function_frames` and managed by a custom `Frame` class, which tracks the function name, variable offsets, and total frame size.

```
High addresses
┌─────────────────────┐
│   Function Args     │  +8(s0), +12(s0), ...  (caller-allocated)
├─────────────────────┤
│   Saved s0          │  +4(s0)
├─────────────────────┤
│   Saved ra          │  0(s0)  ← frame pointer (s0)
├─────────────────────┤
│   Local Variables   │  -4(s0), -8(s0), ...
└─────────────────────┘
Low addresses
```

### Variable Storage

| Variable Type | Location | Notes |
|---|---|---|
| **Local variables** | Stack, negative offsets from `s0` | 4 bytes each, starting at `-4(s0)`; allocated by `Frame.allocate_local` |
| **Function parameters** | Stack, positive offsets from `s0` | Starting at `+8(s0)`; allocated by caller, accessed by callee via `Frame.allocate_param` |
| **Global variables** | `.data` segment with labels | Accessed via `la t0, <label>` + `lw`/`sw` |
| **Structs** | Heap | Heap-allocated via `visit_new_expression`; each variable holds a one-word pointer; field offsets precomputed from `struct_scope` |
| **Constants** | Registers (immediate) | Loaded directly; no constant pool |

### Register Usage

| Register | Purpose |
|---|---|
| `sp` | Stack pointer |
| `s0` | Frame pointer |
| `a0` | Expression results, function return values, left operand in binary expressions |
| `ra` | Return address |
| `t0` | Address computation |
| `t1` | Right operand in binary expressions |

---

## Calling Conventions

### Precall — Caller (`visit_invocation_expression`)

Allocates `8 + (num_args × 4)` bytes on the stack for the return address, saved frame pointer, and arguments. Evaluates and stores each argument at its stack offset, then transfers control to the callee.

### Prologue — Callee (`perform_prologue`)

Saves the caller's `ra` and `s0`, establishes a new frame pointer, and allocates stack space for local variables based on `frame_size`.

### Epilogue — Callee (`perform_epilogue`)

Deallocates local variable space, restores the caller's frame pointer and return address, and returns control to the caller. The return value (if any) is left in `a0`.

### Postcall — Caller (`visit_invocation_expression`)

Deallocates precall stack space by restoring `sp`. The return value remains in `a0` for the caller to use.

---

## Reflection

I am most proud of creating a functional memory-to-memory compiler without needing register allocation to produce working code. The simplicity of this approach allowed me to focus on correctness rather than optimization complexity, and I gained a great deal of understanding about memory allocation and assembly in the process.

Instruction selection was by far the most difficult phase. Managing stack frames, struct field offsets, and the calling convention required careful attention to detail, and debugging assembly was time-consuming.

**What I'd do differently:**

- Implement a proper symbol table class to store function variable and struct field offsets during semantic analysis, rather than computing them manually during code generation
- Add a register allocation and optimization pass
