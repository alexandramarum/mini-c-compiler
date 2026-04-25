from miniast import mini_ast, program_ast, type_ast, statement_ast, expression_ast, lvalue_ast
from miniast.type_ast import ReturnTypeReal, IntType, ReturnTypeVoid, StructType
from miniast.statement_ast import ReturnStatement, ReturnEmptyStatement
from miniast.expression_ast import FalseExpression, TrueExpression, IntegerExpression

class SSASTVisitor(mini_ast.ASTVisitor):

    def __init__(self):
        self.total_errors = 0
        self.global_scope = {}
        self.struct_scope = {}
        self.function_scope = {} 
        self.current_scope = None
        self.current_scope_returns = False
        self.has_main = False

    def error_found(self, msg: str, line: int):
        print(f"ERROR. {msg}. #{line}")
        self.total_errors += 1

    def total_errors_found(self):
        print(f"ERRORS FOUND {self.total_errors}")

    def tree_prefix(self):
        return

    def visit_declaration(self, declaration: program_ast.Declaration):
        if declaration.name.id in self.global_scope:
            self.error_found(f"Invalid redeclaration of {declaration.name.id}", declaration.linenum)
        self.global_scope[declaration.name.id] = declaration
        return

    def visit_type_declaration(self, type_declaration: program_ast.TypeDeclaration):
        self.current_scope = {}

        if type_declaration.name.id in self.struct_scope:
            self.error_found("Struct redeclaration is not allowed", type_declaration.linenum)
        self.struct_scope[type_declaration.name.id] = type_declaration

        for field in type_declaration.fields:
            if field.name.id in self.current_scope:
                self.error_found(f"Struct field name {field.name.id} already in use", field.linenum)
            self.current_scope[field.name.id] = field

            if isinstance(field.type, type_ast.StructType) and field.type.name.id not in self.struct_scope:
                self.error_found(f"Struct {field.name.id} not declared", field.linenum)
        
        self.current_scope = None
        return

    def visit_function(self, function: program_ast.Function):
        self.current_scope = {}

        for param in function.params:
            if param.name.id in self.current_scope:
                self.error_found(f"Parameter {param.name.id} redeclared", param.linenum)
            self.current_scope[param.name.id] = param

        for decl in function.locals:
            if decl.name.id in self.current_scope:
                self.error_found(f"Local var {decl.name.id} redeclared", decl.linenum)
            self.current_scope[decl.name.id] = decl

        # Check for redeclaration of function
        if function.name.id in self.function_scope:
            self.error_found("Function name already in use", function.linenum)
        self.function_scope[function.name.id] = function

        # Special checks for main()
        if function.name.id == "main":
            self.has_main = True
            if len(function.params) != 0:
                self.error_found("Main must not have arguments", function.linenum)
            if not isinstance(function.ret_type, type_ast.IntType):
                self.error_found("Main must return int", function.linenum)
        
        # Check return statements in body
        for stmt in function.body:
            self.visit_statement(stmt)

            if isinstance(stmt, (statement_ast.ReturnStatement, statement_ast.ReturnEmptyStatement)):
                self.current_scope_returns = True

                # Void function
                if isinstance(function.ret_type, type_ast.ReturnTypeVoid):
                    if isinstance(stmt, statement_ast.ReturnStatement) and stmt.expression is not None:
                        self.error_found("Void function must not return a value", stmt.linenum)
                # Non-void function
                else:
                    if isinstance(stmt, statement_ast.ReturnEmptyStatement):
                        # FLAG: non-void function cannot return empty
                        self.error_found("Non-void function must return a value", stmt.linenum)
                    else:  # ReturnStatement with expression
                        expr_type = self.visit_expression(stmt.expression)
                        if type(expr_type) != type(function.ret_type):
                            self.error_found(
                                f"Non-void function must return type {function.ret_type.name.id}; got {type(expr_type).__name__}",
                                stmt.linenum
                            )

        if not self.current_scope_returns and not isinstance(function.ret_type, type_ast.ReturnTypeVoid):
            self.error_found("Non-void function must have a return statement", function.linenum)
        
        self.current_scope = None
        self.current_scope_returns = False
        return

    def visit_program(self, program: program_ast.Program):
        for tdecl in program.types:
            self.visit_type_declaration(tdecl)
        for decl in program.declarations:
            self.visit_declaration(decl)
        for func in program.functions:
            self.visit_function(func)
        
        if not self.has_main:
            self.error_found("Program has no main function", 0)
        
        self.total_errors_found()
        return 

    def visit_type(self, type_: type_ast.Type):
        return type_.accept(self)

    def visit_int_type(self, int_type: type_ast.IntType):
        return int_type

    def visit_bool_type(self, bool_type: type_ast.BoolType):
        return bool_type

    def visit_struct_type(self, struct_type: type_ast.StructType):
        return struct_type
    
    def visit_return_type_real(self, return_type_real: type_ast.ReturnTypeReal):
        return return_type_real
    
    def visit_return_type_void(self, return_type_void) -> mini_ast.Any:
        return return_type_void

    def visit_statement(self, statement: statement_ast.Statement):
        return statement.accept(self)
        
    def visit_assignment_statement(self, assignment_statement: statement_ast.AssignmentStatement, indent=0):
        # Resolve LHS type
        if isinstance(assignment_statement.target, lvalue_ast.LValueID):
            left_type = self.visit_lvalue_id(assignment_statement.target)
        elif isinstance(assignment_statement.target, lvalue_ast.LValueDot):
            left_type = self.visit_lvalue_dot(assignment_statement.target)
        else:
            self.error_found("Unknown assignment target", assignment_statement.linenum)
            return

        # Resolve RHS type
        right_type = self.visit_expression(assignment_statement.source)

        # If LHS type could not be resolved, skip further checks
        if left_type is None:
            return

        # Allow null assignment to structs
        if right_type is None and isinstance(left_type, type_ast.StructType):
            return

        # Check for struct-to-struct assignment
        if isinstance(left_type, type_ast.StructType) and isinstance(right_type, type_ast.StructType):
            if left_type.name.id != right_type.name.id:
                self.error_found(
                    f"Cannot assign struct {right_type.name.id} to struct {left_type.name.id}",
                    assignment_statement.linenum
                )
            return

        # Compare primitive types
        if left_type is not None and right_type is not None and type(left_type) != type(right_type):
            self.error_found(
                f"Cannot assign {type(right_type).__name__} to {type(left_type).__name__}",
                assignment_statement.linenum
            )

    def visit_block_statement(self, block_statement: statement_ast.BlockStatement, indent=0):
        for stmt in block_statement.statements:
            self.visit_statement(stmt)
        return

    def visit_conditional_statement(self, conditional_statement: statement_ast.ConditionalStatement, indent=0):
        outer_scope_returns = self.current_scope_returns
        current_scope_returns = False

        condition_type = self.visit_expression(conditional_statement.guard)
        if not isinstance(condition_type, type_ast.BoolType):
            self.error_found("Condition expression must be boolean", conditional_statement.linenum)
        
        self.current_scope_returns = False
        for stmt in conditional_statement.then_block.statements:
            self.visit_statement(stmt)
        then_returns = self.current_scope_returns

        if conditional_statement.else_block is not None:
            self.current_scope_returns = False
            for stmt in conditional_statement.else_block.statements:
                self.visit_statement(stmt)
            else_returns = self.current_scope_returns
        else:
            else_returns = False

        self.current_scope_returns = outer_scope_returns or (then_returns and else_returns)
        return

    def visit_while_statement(self, while_statement: statement_ast.WhileStatement, indent=0):
        cond_type = self.visit_expression(while_statement.guard)
        if not isinstance(cond_type, type_ast.BoolType):
            self.error_found("While condition must be boolean", while_statement.linenum)

        old_scope_returns = self.current_scope_returns
        self.current_scope_returns = False
        for stmt in while_statement.body.statements:
            self.visit_statement(stmt)
        
        self.current_scope_returns = old_scope_returns
        return

    def visit_delete_statement(self, delete_statement: statement_ast.DeleteStatement, indent=0):
        expr_type = self.visit_expression(delete_statement.expression)
        if not isinstance(expr_type, type_ast.StructType):
            self.error_found("Delete can only be applied to structs", delete_statement.linenum)
        return

    def visit_invocation_statement(self, invocation_statement: statement_ast.InvocationStatement, indent=0):
        self.visit_invocation_expression(invocation_statement.expression)
        return

    def visit_println_statement(self, println_statement: statement_ast.PrintLnStatement, indent=0):
        expr_type = self.visit_expression(println_statement.expression)
        if not isinstance(expr_type, type_ast.IntType):
            self.error_found("Print statement requires an integer", println_statement.linenum)
        return

    def visit_print_statement(self, print_statement: statement_ast.PrintStatement, indent=0):
        expr_type = self.visit_expression(print_statement.expression)
        if not isinstance(expr_type, type_ast.IntType):
            self.error_found("Print statement requires an integer", print_statement.linenum)
        return

    def visit_return_empty_statement(self, return_empty_statement: statement_ast.ReturnEmptyStatement, indent=0):
        self.current_scope_returns = True
        return
    
    def visit_return_statement(self, return_statement: statement_ast.ReturnStatement, indent=0):
        self.current_scope_returns = True
        self.visit_expression(return_statement.expression)
        return

    def visit_expression(self, expression: expression_ast.Expression, indent=0):
        return expression.accept(self, 0)

    def visit_dot_expression(self, dot_expression: expression_ast.DotExpression, indent=0):
        base = self.visit_expression(dot_expression.left)
        
        if isinstance(base, type_ast.StructType):
            struct_decl = self.struct_scope.get(base.name.id)

            if not struct_decl:
                self.error_found(f"Struct {base.name.id} not declared", dot_expression.linenum)
                return
            
            for field in struct_decl.fields:
                if field.name.id == dot_expression.id.id:
                    return field.type
            # Matching declared struct has no field specified by the dot expression
            self.error_found(f"Cannot access field {dot_expression.id.id} of struct {base.name.id}", dot_expression.linenum)
            return
        else:
            # Dot expression can only be used to access struct
            self.error_found(f"Cannot acccess field {dot_expression.id.id} of non-struct type", dot_expression.linenum)
            return

    def visit_false_expression(self, false_expression: expression_ast.FalseExpression, indent=0):
        return type_ast.BoolType()

    def visit_true_expression(self, true_expression: expression_ast.TrueExpression, indent=0):
        return type_ast.BoolType()

    def visit_identifier_expression(self, identifier_expression: expression_ast.IdentifierExpression, indent=0):
        if identifier_expression.id in self.current_scope:
            return self.current_scope[identifier_expression.id].type
        elif identifier_expression.id in self.global_scope:
            return self.global_scope[identifier_expression.id].type
        else:
            self.error_found(f"Variable {identifier_expression.id} not declared", identifier_expression.linenum)
            return type_ast.IntType() # TBD

    def visit_new_expression(self, new_expression: expression_ast.NewExpression, indent=0):
        if new_expression.id.id not in self.struct_scope:
            self.error_found(f"Struct {new_expression.id.id} not declared", new_expression.linenum)
            return None
    
        return type_ast.StructType(name=new_expression.id, linenum=new_expression.linenum)

    def visit_null_expression(self, null_expression: expression_ast.NullExpression, indent=0):
        return None

    def visit_read_expression(self, read_expression: expression_ast.ReadExpression, indent=0):
        return type_ast.IntType()

    def visit_integer_expression(self, integer_expression: expression_ast.IntegerExpression, indent=0):
        return type_ast.IntType()

    def visit_invocation_expression(self, invocation_expression, indent=0):
        func_decl = self.function_scope.get(invocation_expression.name.id)
        if not func_decl:
            self.error_found(f"Function {invocation_expression.name.id} not declared", invocation_expression.linenum)
            return None

        # Check argument count and types
        if len(func_decl.params) != len(invocation_expression.arguments):
            self.error_found(f"Function {func_decl.name.id} called with wrong number of arguments", invocation_expression.linenum)
        else:
            for param, arg in zip(func_decl.params, invocation_expression.arguments):
                arg_type = self.visit_expression(arg)
                if arg_type is None and isinstance(param.type, type_ast.StructType):
                    continue 
                if type(arg_type) != type(param.type):
                    self.error_found(f"Argument type mismatch in call to {func_decl.name.id}", arg.linenum)

        return func_decl.ret_type

    def visit_unary_expression(self, unary_expression: expression_ast.UnaryExpression, indent=0):
        return self.visit_expression(unary_expression.operand)
    
    def visit_binary_expression(self, binary_expression: expression_ast.BinaryExpression, indent=0):
        left = self.visit_expression(binary_expression.left)
        right = self.visit_expression(binary_expression.right)
        op = binary_expression.operator

        int_operators = {
            expression_ast.Operator.PLUS,
            expression_ast.Operator.MINUS,
            expression_ast.Operator.TIMES,
            expression_ast.Operator.DIVIDE
            }
        
        bool_operators = {
            expression_ast.Operator.AND,
            expression_ast.Operator.OR
        }

        quant_comp_operators = {
            expression_ast.Operator.LT,
            expression_ast.Operator.LE,
            expression_ast.Operator.GT,
            expression_ast.Operator.GE
        }

        qual_comp_operators = {
            expression_ast.Operator.EQ,
            expression_ast.Operator.NE
        }

        if op in int_operators:
            if not isinstance(left, type_ast.IntType) or not isinstance(right, type_ast.IntType):
                self.error_found("Operands must be ints", binary_expression.linenum)
                return None
            return type_ast.IntType()
        
        if op in bool_operators:
            if not isinstance(left, type_ast.BoolType) or not isinstance(right, type_ast.BoolType):
                self.error_found("Operands must be bools", binary_expression.linenum)
                return None
            return type_ast.BoolType()
        
        if op in quant_comp_operators:
            if not isinstance(left, type_ast.IntType) or not isinstance(right, type_ast.IntType):
                self.error_found("Operands must be int", binary_expression.linenum)
                return None
            return type_ast.BoolType()
        
        if op in qual_comp_operators:
            return type_ast.BoolType()
        
        self.error_found("Unknown operator", binary_expression.linenum)
        return

    def visit_lvalue(self, lvalue: lvalue_ast.LValue, indent=0):
        return lvalue.accept(self)
        
    def visit_lvalue_dot(self, lvalue_dot: lvalue_ast.LValueDot, indent=0):
        # Get base type (LHS)
        base_type = self.visit_lvalue(lvalue_dot.left)
        
        if not isinstance(base_type, type_ast.StructType):
            self.error_found(
                f"Cannot access field {lvalue_dot.id.id} of non-struct type",
                lvalue_dot.linenum
            )
            return None

        struct_decl = self.struct_scope.get(base_type.name.id)
        if struct_decl is None:
            self.error_found(f"Struct {base_type.name.id} not declared", lvalue_dot.linenum)
            return None

        # Look for the field
        for field in struct_decl.fields:
            if field.name.id == lvalue_dot.id.id:
                return field.type

        self.error_found(f"Struct {base_type.name.id} has no field {lvalue_dot.id.id}", lvalue_dot.linenum)
        return None

    def visit_lvalue_id(self, lvalue_id: lvalue_ast.LValueID, indent=0):
        # First check current function scope
        if self.current_scope and lvalue_id.id.id in self.current_scope:
            return self.current_scope[lvalue_id.id.id].type
        # Then check global scope
        elif lvalue_id.id.id in self.global_scope:
            return self.global_scope[lvalue_id.id.id].type
        else:
            self.error_found(f"Variable {lvalue_id.id.id} not declared", lvalue_id.linenum)
            return type_ast.IntType()

    