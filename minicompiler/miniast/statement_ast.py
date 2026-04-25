from miniast import mini_ast, expression_ast, lvalue_ast

class Statement(mini_ast.MiniASTNode):
    """The abstract Statement in a .mini AST"""

    def __init__(self, linenum : int):
        self.linenum = linenum

    #def accept(self, visitor: mini_ast.ASTVisitor):
    #    return visitor.visit_statement(self)

class AssignmentStatement(Statement):
    """The Assignment statement in a .mini AST."""

    def __init__(self, linenum : int, target : lvalue_ast.LValue, source : expression_ast.Expression):
        super().__init__(linenum)
        self.target = target
        self.source = source

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_assignment_statement(self, indent)

class BlockStatement(Statement):
    """The Block statement in a .mini AST."""

    def __init__(self, linenum : int, statements : list[Statement]):
        super().__init__(linenum)
        self.statements = statements

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_block_statement(self, indent)

    # This is from the Java implementation and was a static method. 
    # I think we don't need it -- could just call BlockStatement(-1,[]) whereever an empty block is needed?  
    """def empty_block(self):
        # Return an empty Block statement.

        emp_block = BlockStatement(-1,[])
        return emp_block
    """

class ConditionalStatement(Statement):
    """The If statement in a .mini AST."""
    def __init__(self, linenum : int, guard : expression_ast.Expression, then_block : BlockStatement, else_block : BlockStatement):
        super().__init__(linenum)
        self.guard = guard
        self.then_block = then_block
        self.else_block = else_block

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_conditional_statement(self, indent)

class WhileStatement(Statement):
    """The While statement in a .mini AST."""

    def __init__(self, linenum: int, guard : expression_ast.Expression, body: Statement):
        super().__init__(linenum)
        self.guard = guard
        self.body = body

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_while_statement(self, indent)

class DeleteStatement(Statement):
    """The Delete statement in a .mini AST."""

    def __init__(self, linenum : int, expression : expression_ast.Expression):
        super().__init__(linenum)
        self.expression = expression

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_delete_statement(self, indent)

class InvocationStatement(Statement):
    """The Invocation statement in a .mini AST."""

    def __init__(self, linenum: int, expression : expression_ast.InvocationExpression):
        super().__init__(linenum)
        self.expression = expression

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_invocation_statement(self, indent)

class PrintLnStatement(Statement):
    """The PrintLn statement in a .mini AST."""

    def __init__(self, linenum: int, expression : expression_ast.Expression):
        super().__init__(linenum)
        self.expression = expression

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_println_statement(self, indent)

class PrintStatement(Statement):
    """The Print statement in a .mini AST."""

    def __init__(self, linenum: int, expression : expression_ast.Expression):
        super().__init__(linenum)
        self.expression = expression

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_print_statement(self, indent)

class ReturnEmptyStatement(Statement):
    """The ReturnEmpty statement in a .mini AST."""

    def __init__(self, linenum: int):
        super().__init__(linenum)

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_return_empty_statement(self, indent)

class ReturnStatement(Statement):
    """The Return statement in a .mini AST."""

    def __init__(self, linenum: int, expression : expression_ast.Expression):
        super().__init__(linenum)
        self.expression = expression # expression may be None

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_return_statement(self, indent)
