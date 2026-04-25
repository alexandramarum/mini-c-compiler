### Write-up
In my implementation of the static semantic analysis AST visitor, I made no changes to the AST, nor did I use a different intermediate representation. I represented the symbol tables as dictionary properties of the visitor and included four types of scopes:

- global_scope: tracks global variable declarations
- struct_scope: tracks struct type declarations
- function_scope: tracks function declarations
- current_scope: tracks variables and parameters local to the current function


When entering a new function or struct scope, current_scope is initialized for the duration of the traversal to detect errors and is reset upon completion. This approach works because Mini does not allow nested function declarations, so current_scope will never be incorrectly overwritten when analyzing a function body.