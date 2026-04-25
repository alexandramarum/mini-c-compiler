from miniast import mini_ast, expression_ast

class Type(mini_ast.MiniASTNode):
    #def accept(self, visitor: mini_ast.ASTVisitor):
    #    return visitor.visit_type(self)
    pass

class IntType(Type):
    def accept(self, visitor: mini_ast.ASTVisitor):
        return visitor.visit_int_type(self)

class BoolType(Type):
    def accept(self, visitor: mini_ast.ASTVisitor):
        return visitor.visit_bool_type(self)

#class VoidType(Type):
#    def accept(self, visitor: mini_ast.ASTVisitor):
#        return visitor.visit_void_type(self)

class StructType(Type):
    """Struct Types in a .mini AST"""

    def __init__(self, linenum : int, name : expression_ast.IdentifierExpression):
        self.linenum = linenum
        self.name = name

    def accept(self, visitor: mini_ast.ASTVisitor):
        return visitor.visit_struct_type(self)
    
class ReturnType(mini_ast.MiniASTNode):
    pass

class ReturnTypeReal(ReturnType):
    def __init__(self, type_: Type):
        self.type_ = type_

    def accept(self, visitor: mini_ast.ASTVisitor):
        return visitor.visit_return_type_real(self)
    
class ReturnTypeVoid(ReturnType):
    def accept(self, visitor: mini_ast.ASTVisitor):
        return visitor.visit_return_type_void(self)
