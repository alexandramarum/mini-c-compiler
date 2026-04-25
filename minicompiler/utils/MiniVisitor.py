# Generated from Mini.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .MiniParser import MiniParser
else:
    from MiniParser import MiniParser

# This class defines a complete generic visitor for a parse tree produced by MiniParser.

class MiniVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MiniParser#program.
    def visitProgram(self, ctx:MiniParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#types.
    def visitTypes(self, ctx:MiniParser.TypesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#typeDeclaration.
    def visitTypeDeclaration(self, ctx:MiniParser.TypeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#nestedDecl.
    def visitNestedDecl(self, ctx:MiniParser.NestedDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#decl.
    def visitDecl(self, ctx:MiniParser.DeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#IntType.
    def visitIntType(self, ctx:MiniParser.IntTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#BoolType.
    def visitBoolType(self, ctx:MiniParser.BoolTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#StructType.
    def visitStructType(self, ctx:MiniParser.StructTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#declarations.
    def visitDeclarations(self, ctx:MiniParser.DeclarationsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#declaration.
    def visitDeclaration(self, ctx:MiniParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#functions.
    def visitFunctions(self, ctx:MiniParser.FunctionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#function.
    def visitFunction(self, ctx:MiniParser.FunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#parameters.
    def visitParameters(self, ctx:MiniParser.ParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#ReturnTypeReal.
    def visitReturnTypeReal(self, ctx:MiniParser.ReturnTypeRealContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#ReturnTypeVoid.
    def visitReturnTypeVoid(self, ctx:MiniParser.ReturnTypeVoidContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#NestedBlock.
    def visitNestedBlock(self, ctx:MiniParser.NestedBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#Assignment.
    def visitAssignment(self, ctx:MiniParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#Print.
    def visitPrint(self, ctx:MiniParser.PrintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#PrintLn.
    def visitPrintLn(self, ctx:MiniParser.PrintLnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#Conditional.
    def visitConditional(self, ctx:MiniParser.ConditionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#While.
    def visitWhile(self, ctx:MiniParser.WhileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#Delete.
    def visitDelete(self, ctx:MiniParser.DeleteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#Return.
    def visitReturn(self, ctx:MiniParser.ReturnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#Invocation.
    def visitInvocation(self, ctx:MiniParser.InvocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#block.
    def visitBlock(self, ctx:MiniParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#statementList.
    def visitStatementList(self, ctx:MiniParser.StatementListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#LvalueId.
    def visitLvalueId(self, ctx:MiniParser.LvalueIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#LvalueDot.
    def visitLvalueDot(self, ctx:MiniParser.LvalueDotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#IntegerExpr.
    def visitIntegerExpr(self, ctx:MiniParser.IntegerExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#TrueExpr.
    def visitTrueExpr(self, ctx:MiniParser.TrueExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#IdentifierExpr.
    def visitIdentifierExpr(self, ctx:MiniParser.IdentifierExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#BinaryExpr.
    def visitBinaryExpr(self, ctx:MiniParser.BinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#NewExpr.
    def visitNewExpr(self, ctx:MiniParser.NewExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#NestedExpr.
    def visitNestedExpr(self, ctx:MiniParser.NestedExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#DotExpr.
    def visitDotExpr(self, ctx:MiniParser.DotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#UnaryExpr.
    def visitUnaryExpr(self, ctx:MiniParser.UnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#InvocationExpr.
    def visitInvocationExpr(self, ctx:MiniParser.InvocationExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#FalseExpr.
    def visitFalseExpr(self, ctx:MiniParser.FalseExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#NullExpr.
    def visitNullExpr(self, ctx:MiniParser.NullExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniParser#arguments.
    def visitArguments(self, ctx:MiniParser.ArgumentsContext):
        return self.visitChildren(ctx)



del MiniParser