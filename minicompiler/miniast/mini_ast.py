#from miniast import program_ast, type_ast, statement_ast, expression_ast, lvalue_ast 
from typing import Any
from abc import ABC, abstractmethod

class MiniASTNode():
    #    def accept(self, visitor):
    #       pass
    pass

class ASTVisitor(ABC):
    @abstractmethod
    def visit_declaration(self, declaration) -> Any:
        """Visit a program_ast.Declaration node."""
        pass

    @abstractmethod
    def visit_type_declaration(self, type_declaration) -> Any:
        """Visit a program_ast.TypeDeclaration node."""
        pass

    @abstractmethod
    def visit_function(self, function) -> Any:
        """Visit a program_ast.Function node."""
        pass

    @abstractmethod
    def visit_program(self, program) -> Any:
        """Visit a program_ast.Program node."""
        pass

    @abstractmethod
    def visit_int_type(self, int_type) -> Any:
        """Visit a type_ast.IntType node."""
        pass

    @abstractmethod
    def visit_bool_type(self, bool_type) -> Any:
        """Visit a type_ast.BoolType node."""
        pass

    @abstractmethod
    def visit_struct_type(self, struct_type) -> Any:
        """Visit a type_ast.StructType node."""
        pass

    @abstractmethod
    def visit_return_type_real(self, return_type_real) -> Any:
        """Visit a type_ast.ReturnTypeReal"""
        pass

    @abstractmethod
    def visit_return_type_void(self, return_type_void) -> Any:
        """Visit a type_ast.ReturnTypeVoid"""
        pass


    @abstractmethod
    def visit_assignment_statement(self, assignment_statement) -> Any:
        """Visit a statement_ast.AssignmentStatement node."""
        pass

    @abstractmethod
    def visit_block_statement(self, block_statement) -> Any:
        """Visit a statement_ast.BlockStatement node."""
        pass

    @abstractmethod
    def visit_conditional_statement(self, conditional_statement) -> Any:
        """Visit a statement_ast.ConditionalStatement node."""
        pass

    @abstractmethod
    def visit_while_statement(self, while_statement) -> Any:
        """Visit a statement_ast.WhileStatement node."""
        pass

    @abstractmethod
    def visit_delete_statement(self, delete_statement) -> Any:
        """Visit a statement_ast.DeleteStatement node."""
        pass

    @abstractmethod
    def visit_invocation_statement(self, invocation_statement) -> Any:
        """Visit a statement_ast.InvocationStatement node."""
        pass

    @abstractmethod
    def visit_println_statement(self, println_statement) -> Any:
        """Visit a statement_ast.PrintLnStatement node."""
        pass

    @abstractmethod
    def visit_print_statement(self, print_statement) -> Any:
        """Visit a statement_ast.PrintStatement node."""
        pass

    @abstractmethod
    def visit_return_empty_statement(self, return_empty_statement) -> Any:
        """Visit a statement_ast.ReturnEmptyStatement node."""
        pass

    @abstractmethod
    def visit_return_statement(self, return_statement) -> Any:
        """Visit a statement_ast.ReturnStatement node."""
        pass

    @abstractmethod
    def visit_dot_expression(self, dot_expression) -> Any:
        """Visit an expression_ast.DotExpression node"""
        pass

    @abstractmethod
    def visit_false_expression(self, false_expression) -> Any:
        """Visit an expression_ast.FalseExpression node."""
        pass

    @abstractmethod
    def visit_true_expression(self, true_expression) -> Any:
        """Visit an expression_ast.TrueExpression node."""
        pass

    @abstractmethod
    def visit_identifier_expression(self, identifier_expression) -> Any:
        """Visit an expression_ast.IdentifierExpression node."""
        pass

    @abstractmethod
    def visit_new_expression(self, new_expression) -> Any:
        """Visit an expression_ast.NewExpression node."""
        pass

    @abstractmethod
    def visit_null_expression(self, null_expression) -> Any:
        """Visit an expression_ast.NullExpression node."""
        pass

    @abstractmethod
    def visit_read_expression(self, read_expression) -> Any:
        """Visit an expression_ast.ReadExpression node."""
        pass

    @abstractmethod
    def visit_integer_expression(self, integer_expression) -> Any:
        """Visit an expression_ast.IntegerExpression node."""
        pass

    @abstractmethod
    def visit_invocation_expression(self, invocation_expression) -> Any:
        """Visit an expression_ast.InvocationExpression node."""
        pass

    @abstractmethod
    def visit_unary_expression(self, unary_expression) -> Any:
        """Visit an expression_ast.UnaryExpression node."""
        pass

    @abstractmethod
    def visit_binary_expression(self, binary_expression) -> Any:
        """Visit an expression_ast.BinaryExpression node."""
        pass

    @abstractmethod
    def visit_lvalue_dot(self, lvalue_dot) -> Any:
        """Visit a lvalue_ast.LValueDot node."""
        pass

    @abstractmethod
    def visit_lvalue_id(self, lvalue_id) -> Any:
        """Visit a lvalue_ast.LValueID node."""
        pass
    