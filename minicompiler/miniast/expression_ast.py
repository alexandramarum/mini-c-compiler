from enum import Enum
from miniast import mini_ast

class Operator(Enum):
    TIMES = "*"
    DIVIDE = "/"
    PLUS = "+"
    MINUS = "-"
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    EQ = "=="
    NE = "!="
    AND = "&&"
    OR = "||"
    NOT = "!"
    ERR = "UNKNOWN"


class Expression(mini_ast.MiniASTNode):
    """The abstract Expression in a .mini AST."""

    #def accept(self, visitor: mini_ast.ASTVisitor):
    #    return visitor.visit_expression(self)
        
class IdentifierExpression(Expression):
    """The Expression for ID values in a .mini AST."""

    def __init__(self, linenum: int, id: str):
        self.linenum = linenum
        self.id = id

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_identifier_expression(self, indent)

class DotExpression(Expression):
    """The Expression for dotted names in a .mini AST."""

    def __init__(self, linenum: int, left: Expression, id: IdentifierExpression):
        self.linenum = linenum
        self.left = left # a DotExpression or IdentifierExpression
        self.id = id

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_dot_expression(self, indent)

class FalseExpression(Expression):
    """The Expression for False in a .mini AST."""

    def __init__(self, linenum: int):
        self.linenum = linenum

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_false_expression(self, indent)

class TrueExpression(Expression):
    """The Expression for True in a .mini AST."""

    def __init__(self, linenum: int):
        self.linenum = linenum

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_true_expression(self, indent)

class NewExpression(Expression):
    """The Expression to allocate a new struct in a .mini AST."""

    def __init__(self, linenum: int, id: IdentifierExpression):
        self.linenum = linenum
        self.id = id

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_new_expression(self, indent)

class NullExpression(Expression):
    """The Expression for a null value in a .mini AST."""

    def __init__(self, linenum: int):
        self.linenum = linenum

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_null_expression(self, indent)

class ReadExpression(Expression):
    """The Expression to read from stdin in a .mini AST."""

    def __init__(self, linenum: int):
        self.linenum = linenum

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_read_expression(self, indent)

class IntegerExpression(Expression):
    """The Expression for an int in a .mini AST."""

    def __init__(self, linenum: int, value: str):
        self.linenum = linenum
        self.value = value

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_integer_expression(self, indent)

class InvocationExpression(Expression):
    """The Expression for a function call in a .mini AST."""

    def __init__(self, linenum: int, name: IdentifierExpression, arguments: list[Expression]):
        self.linenum = linenum
        self.name = name
        self.arguments = arguments

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_invocation_expression(self, indent)


# The java version has a separate Create method that takes in a string as an operator. I just do it all here in the init.
class UnaryExpression(Expression):
    """The Expression for unary operations in a .mini AST."""

    def __init__(self, linenum: int, operator: Operator | str, operand: Expression):
        self.linenum = linenum
        self.operand = operand

        if isinstance(operator, Operator):
            self.operator = operator
        elif isinstance(operator, str):
            match operator:
                case '!':
                    op_oper = Operator.NOT
                case '-':
                    op_oper = Operator.MINUS
                case _:
                    print('WEIRD operator string', operator)
                    op_oper = Operator.ERR
            self.operator = op_oper
        else:
            print("WEIRD operator type", operator.__class__)

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_unary_expression(self, indent)


# The java version has a separate Create method that takes in a string as an operator. I just do it all here in the init.
class BinaryExpression(Expression):
    """The binary Expression in a .mini AST."""

    def __init__(self, linenum: int, operator: Operator | str, left: Expression, right: Expression):
        self.linenum = linenum
        self.left = left
        self.right = right

        if isinstance(operator, Operator):
            self.operator = operator
        elif isinstance(operator, str):
            match operator:
                case '*':
                    op_oper = Operator.TIMES
                case '/':
                    op_oper = Operator.DIVIDE
                case '+':
                    op_oper = Operator.PLUS
                case '-':
                    op_oper = Operator.MINUS
                case '<':
                    op_oper = Operator.LT
                case '<=':
                    op_oper = Operator.LE
                case '>':
                    op_oper = Operator.GT
                case '>=':
                    op_oper = Operator.GE
                case '==':
                    op_oper = Operator.EQ
                case '!=':
                    op_oper = Operator.NE
                case '&&':
                    op_oper = Operator.AND
                case '||':
                    op_oper = Operator.OR
                case _:
                    print("WEIRD operator string", operator)
                    op_oper = Operator.ERR
            self.operator = op_oper
        else:
            print("WEIRD operator type:", operator.__class__)

    def accept(self, visitor: mini_ast.ASTVisitor, indent=0):
        return visitor.visit_binary_expression(self, indent)
