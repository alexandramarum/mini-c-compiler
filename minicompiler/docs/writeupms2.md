### Milestone 2 Writeup

In this milestone, I implemented the ISASTVisitor to handle instruction selection and code generation for the Mini-C compiler.

The ISASTVisitor is designed as a syntax-directed translator, visting each node in the AST and directly emitting its RISC-V assembly instructions. This design keeps the structure simple to implement and understand.

The visitor uses a memory-to-memory model, generating functional code in a single pass over the AST without the need for unlimited registers or a register allocation pass. Instead, it simply stores and loads values from memory as needed and spills values to the stack during complex expressions and between operations.

The following registers are used in the code generation:
-   **a0**: The result of every expression is left in a0.
-   **t0, t1**: Used as temporary registers for intermediate calculations
-   **s0**: Frame pointer.
-   **sp**: Stack pointer.
-   **ra**: Return address.

The visitor also generates function frames and struct offsets at the beginning of the program to manage memory use and access.

Higher addresses
+------------------+
| ...              |
| Argument 1       |  +8 from s0
+------------------+
| Return address   |  +4 from s0
| Saved s0         |  0 from s0  ← s0 points here
+------------------+
| Local var 1      |  -4 from s0
| ...              |
+------------------+  ← sp points here
Lower addresses


