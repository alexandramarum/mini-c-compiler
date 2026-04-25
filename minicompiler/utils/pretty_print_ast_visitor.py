from miniast import mini_ast, program_ast, type_ast, statement_ast, expression_ast, lvalue_ast

class PPASTVisitor(mini_ast.ASTVisitor):
    """Print the AST using indentation to show its structure."""

    def tree_prefix(self, indent, is_last):
        if indent == 0:
            return ""
        return ("│   " * (indent - 1)) + ("└── " if is_last else "├── ")

    def visit_declaration(self, declaration: program_ast.Declaration, indent=0):
        return f"{self.tree_prefix(indent, True)}DECL: {self.visit_type(declaration.type)} {declaration.name.id};\n"

    def visit_type_declaration(self, type_declaration: program_ast.TypeDeclaration, indent):
        for declaration in type_declaration.fields:
            output = f"{self.tree_prefix(indent, False)}struct {type_declaration.name.id}\n"
        for declaration in type_declaration.fields:
            output += self.visit_declaration(declaration, indent + 1)
        return output

    def visit_function(self, function: program_ast.Function, indent=0):
        params = ", ".join(f"{self.visit_type(p.type)} {p.name.id}" for p in function.params)
        output = f"{self.tree_prefix(indent, False)}fun {function.name.id}({params}) {self.visit_type(function.ret_type)}\n"
        for decl in function.locals:
            output += self.visit_declaration(decl, indent + 1)
        for stmt in function.body:
            output += self.visit_statement(stmt, indent + 1)
        return output + "\n"

    def visit_program(self, program: program_ast.Program, indent=0):
        program_str = "Type (Struct) Declarations:\n"

        for tdecls in program.types:
            program_str += self.visit_type_declaration(tdecls, indent+1)
        program_str += "Declarations:\n"
        for decls in program.declarations:
            program_str += self.visit_declaration(decls, indent+1)
        program_str += "\nFunctions:\n"
        for funcs in program.functions:
            program_str += self.visit_function(funcs, indent+1)
        return program_str

    def visit_type(self, type_: type_ast.Type):
        return type_.accept(self)

    def visit_int_type(self, int_type: type_ast.IntType):
        return "int"

    def visit_bool_type(self, bool_type: type_ast.BoolType):
        return "bool"

    def visit_struct_type(self, struct_type: type_ast.StructType):
        return f"struct {struct_type.name.id}"
    
    def visit_return_type_real(self, return_type_real: type_ast.ReturnTypeReal, indent=0):
        return f"RETURNTYPE: {return_type_real.type_}"
    
    def visit_return_type_void(self, return_type_void) -> mini_ast.Any:
        return f"RETURNTYPE: void"

    def visit_statement(self, statement: statement_ast.Statement, indent=0):
        return statement.accept(self, indent)
        
    def visit_assignment_statement(self, assignment_statement: statement_ast.AssignmentStatement, indent=0):
        output = f"{self.tree_prefix(indent, True)}ASSN:\n"
        output += self.visit_lvalue(assignment_statement.target, indent + 1) + "\n"
        output += f"{self.tree_prefix(indent + 1, True)}OP: = \n"
        output += self.visit_expression(assignment_statement.source, indent + 1) + "\n"
        return output


    def visit_block_statement(self, block_statement: statement_ast.BlockStatement, indent=0):
        output = f"{self.tree_prefix(indent, False)}BLOCK:\n"
        for stmt in block_statement.statements:
            output += self.visit_statement(stmt, indent + 1)
        return output

    def visit_conditional_statement(self, conditional_statement: statement_ast.ConditionalStatement, indent=0):
        output = f"{self.tree_prefix(indent, False)}IF:\n"
        output += self.visit_expression(conditional_statement.guard, indent + 1) + "\n"
        output += f"{self.tree_prefix(indent, False)}THEN:\n"
        output += self.visit_block_statement(conditional_statement.then_block, indent + 1)
        if conditional_statement.else_block:
            output += f"{self.tree_prefix(indent, False)}ELSE:\n"
            output += self.visit_block_statement(conditional_statement.else_block, indent + 1)
        return output

    def visit_while_statement(self, while_statement: statement_ast.WhileStatement, indent=0):
        output = f"{self.tree_prefix(indent, False)}WHILE:\n"
        output += self.visit_expression(while_statement.guard, indent + 1) + "\n"
        output += self.visit_statement(while_statement.body, indent + 1)
        return output

    def visit_delete_statement(self, delete_statement: statement_ast.DeleteStatement, indent=0):
        output = f"{self.tree_prefix(indent, False)}DELETE:\n"
        output += self.visit_expression(delete_statement.expression, indent + 1) + "\n"
        return output

    def visit_invocation_statement(self, invocation_statement: statement_ast.InvocationStatement, indent=0):
        output = f"{self.tree_prefix(indent, False)}CALL:\n"
        output += self.visit_invocation_expression(invocation_statement.expression, indent + 1) + "\n"
        return output

    def visit_println_statement(self, println_statement: statement_ast.PrintLnStatement, indent=0):
        expr_str = self.visit_expression(println_statement.expression)
        return f"{self.tree_prefix(indent, False)}PRINTLN: {expr_str}\n"

    def visit_print_statement(self, print_statement: statement_ast.PrintStatement, indent=0):
        expr_str = self.visit_expression(print_statement.expression, indent + 1)
        return f"{self.tree_prefix(indent, False)}PRINT:\n{expr_str}\n"

    def visit_return_empty_statement(self, return_empty_statement: statement_ast.ReturnEmptyStatement, indent=0):
        return f"{self.tree_prefix(indent, False)}RETURN;\n"
    
    def visit_return_statement(self, return_statement: statement_ast.ReturnStatement, indent=0):
        if return_statement.expression:
            expr_str = self.visit_expression(return_statement.expression, indent + 1)
            return f"{self.tree_prefix(indent, False)}RETURN:\n{expr_str}\n"
        else:
            return f"{self.tree_prefix(indent, False)}RETURN;\n"

    def visit_expression(self, expression: expression_ast.Expression, indent=0):
        return f"{self.tree_prefix(indent, True)}EXPR:\n{expression.accept(self, indent + 1)}"

    def visit_dot_expression(self, dot_expression: expression_ast.DotExpression, indent=0):
        base_str = self.visit_expression(dot_expression.left, indent + 1)
        return f"{base_str}\n{self.tree_prefix(indent, True)}DOT_EXPR: {dot_expression.id.id}"

    def visit_false_expression(self, false_expression: expression_ast.FalseExpression, indent=0):
        return f"{self.tree_prefix(indent, True)}BOOL: false"

    def visit_true_expression(self, true_expression: expression_ast.TrueExpression, indent=0):
        return f"{self.tree_prefix(indent, True)}BOOL: true"

    def visit_identifier_expression(self, identifier_expression: expression_ast.IdentifierExpression, indent=0):
        return f"{self.tree_prefix(indent, True)}ID: {identifier_expression.id}"

    def visit_new_expression(self, new_expression: expression_ast.NewExpression, indent=0):
        return f"{self.tree_prefix(indent, True)}NEW: {new_expression.id, indent+1}"

    def visit_null_expression(self, null_expression: expression_ast.NullExpression, indent=0):
        return f"{self.tree_prefix(indent, True)}NULL"

    def visit_read_expression(self, read_expression: expression_ast.ReadExpression, indent=0):
        return f"{self.tree_prefix(indent, True)}READ"

    def visit_integer_expression(self, integer_expression: expression_ast.IntegerExpression, indent=0):
        return f"{self.tree_prefix(indent, True)}INT: {integer_expression.value}"

    def visit_invocation_expression(self, invocation_expression: expression_ast.InvocationExpression, indent=0):
        args_str = ""
        for arg in invocation_expression.arguments:
            args_str += self.visit_expression(arg, indent + 1) + "\n"
        return f"{self.tree_prefix(indent, True)}CALL: {invocation_expression.name.id}\n{args_str.rstrip()}"

    def visit_unary_expression(self, unary_expression: expression_ast.UnaryExpression, indent=0):
        operand_str = self.visit_expression(unary_expression.operand, indent + 1)
        ops = ' '.join(unary_expression.operator.name)
        return f"{self.tree_prefix(indent, True)}UNARY: {ops}\n{operand_str}"
    
    def visit_binary_expression(self, binary_expression: expression_ast.BinaryExpression, indent=0):
        left_str = self.visit_expression(binary_expression.left, indent + 1)
        right_str = self.visit_expression(binary_expression.right, indent + 1)
        op = binary_expression.operator.name
        return f"{self.tree_prefix(indent, True)}BINARY: {op}\n{left_str}\n{right_str}"

    def visit_lvalue(self, lvalue: lvalue_ast.LValue, indent=0):
        return lvalue.accept(self, indent)
        
    def visit_lvalue_dot(self, lvalue_dot: lvalue_ast.LValueDot, indent=0):
        base_str = self.visit_lvalue(lvalue_dot.left, indent)
        return f"{base_str}\n{self.tree_prefix(indent, True)}LVALDOT: {lvalue_dot.id.id}"

    def visit_lvalue_id(self, lvalue_id: lvalue_ast.LValueID, indent=0):
        return f"{self.tree_prefix(indent, True)}LVAL: {lvalue_id.id.id}"
    