from miniast import mini_ast, expression_ast

class LValue(mini_ast.MiniASTNode):
    """The left-hand side of an assign statement in a .mini AST."""

    def __init__(self, linenum : int):
        self.linenum = linenum
        
    #def accept(self, visitor: mini_ast.ASTVisitor):
    #    return visitor.visit_lvalue(self)
    
class LValueDot(LValue):
    """A dotted name for the LValue in a .mini AST."""

    def __init__(self, linenum: int, left: LValue, id: expression_ast.IdentifierExpression):
        super().__init__(linenum)
        self.left = left 
        self.id = id

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_lvalue_dot(self, indent)

class LValueID(LValue):
    """An ID for the LValue in a .mini AST."""

    def __init__(self, linenum: int, id: expression_ast.IdentifierExpression):
        super().__init__(linenum)
        self.id = id

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_lvalue_id(self, indent)