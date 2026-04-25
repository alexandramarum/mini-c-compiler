from miniast import mini_ast, type_ast, statement_ast, expression_ast

class Declaration(mini_ast.MiniASTNode):
    """Declares variables in a .mini AST."""
    
    def __init__(self, linenum: int, type: type_ast.Type, name: expression_ast.IdentifierExpression):
        self.linenum = linenum
        self.type = type
        self.name = name

    def accept(self, visitor: mini_ast.ASTVisitor):
        return visitor.visit_declaration(self)

class TypeDeclaration(mini_ast.MiniASTNode):
    """Declares structs in a .mini AST."""
    
    def __init__(self, linenum: int, name: expression_ast.IdentifierExpression, fields: list[Declaration]):
        self.linenum = linenum
        self.name = name
        self.fields = fields

    def accept(self, visitor: mini_ast.ASTVisitor):
        return visitor.visit_type_declaration(self)

class Function(mini_ast.MiniASTNode):
    """Function definitions in a .mini AST."""
    
    def __init__(self, linenum: int, name: expression_ast.IdentifierExpression, ret_type: type_ast.Type, 
                 params: list[Declaration], locals: list[Declaration], body: list[statement_ast.Statement]):
        self.linenum = linenum
        self.name = name
        self.ret_type = ret_type
        self.params = params
        self.locals = locals
        self.body = body

    def accept(self, visitor: mini_ast.ASTVisitor):
        return visitor.visit_function(self)

class Program(mini_ast.MiniASTNode):
    """The top-level program object in a .mini AST."""

    def __init__(self, types: list[TypeDeclaration] = [], declarations: list[Declaration] = [], 
                 functions: list[Function] = []):
        self.types = types
        self.declarations = declarations
        self.functions = functions

    def accept(self, visitor: mini_ast.ASTVisitor):
        return visitor.visit_program(self)
