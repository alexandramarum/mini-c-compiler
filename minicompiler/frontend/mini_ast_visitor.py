from miniast import program_ast, type_ast, statement_ast, expression_ast, lvalue_ast
from antlr4 import *
from MiniParser import MiniParser
from MiniVisitor import MiniVisitor

class MiniToASTVisitor(MiniVisitor):
    """Produce the AST of a .mini program from its parse-tree."""

    def __init__(self):
        self.program_ast = program_ast.Program()

    def visitProgram(self, ctx:MiniParser.ProgramContext):
        """Visit a .mini parse tree produced by the MiniParser parser.program()."""
        self.program_ast.types = self.visit(ctx.types())
        self.program_ast.declarations = self.visit(ctx.declarations())
        self.program_ast.functions = self.visit(ctx.functions())

        return self.program_ast
    
    def visitDeclarations(self, ctx: MiniParser.DeclarationsContext):
        declarations = []
        for declaration_ctx in ctx.declaration():
            declarations.extend(self._add_declarations(declaration_ctx))

        return declarations
    
    def _add_declarations(self, ctx: MiniParser.DeclarationContext):
        declarations = []

        type = self.visit(ctx.type_()) 
        for idnode in ctx.ID():
             id_name = expression_ast.IdentifierExpression(ctx.start.line, idnode.getText())
             declaration = program_ast.Declaration(ctx.start.line, type, id_name)
             declarations.append(declaration)

        return declarations

    # Visit a parse tree produced by MiniParser#declaration.
    def visitDeclaration(self, ctx:MiniParser.DeclarationContext):
        print("VisitDeclaration -- WEIRD")
        return self.visitChildren(ctx)    

    # Visit a parse tree produced by MiniParser#types.
    def visitTypes(self, ctx:MiniParser.TypesContext):
        types = []
        for type_declaration_ctx in ctx.typeDeclaration():
            types.append(self.visit(type_declaration_ctx))
        return types

    # Visit a parse tree produced by MiniParser#typeDeclaration.
    def visitTypeDeclaration(self, ctx:MiniParser.TypeDeclarationContext):
        fields = self.visit(ctx.nestedDecl())
        name = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        type_declaration = program_ast.TypeDeclaration(ctx.start.line, name, fields)
        return type_declaration

    # Visit a parse tree produced by MiniParser#nestedDecl.
    def visitNestedDecl(self, ctx:MiniParser.NestedDeclContext):
        nested_decls = []
        for decl_ctx in ctx.decl():
            nested_decls.append(self.visit(decl_ctx))
        return nested_decls

    # Visit a parse tree produced by MiniParser#decl.
    def visitDecl(self, ctx:MiniParser.DeclContext):
        id_name = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        declaration = program_ast.Declaration(ctx.start.line, self.visit(ctx.type_()), id_name)
        return declaration

     # Visit a parse tree produced by MiniParser#functions.
    def visitFunctions(self, ctx:MiniParser.FunctionsContext):
        functions = []
        for function_ctx in ctx.function():
            functions.append(self.visit(function_ctx))
        return functions

    # Visit a parse tree produced by MiniParser#function.
    def visitFunction(self, ctx:MiniParser.FunctionContext):

        return_type = self.visit(ctx.returnType())
        parameters = self.visit(ctx.parameters())
        locals = self.visit(ctx.declarations())
        body = self.visit(ctx.statementList())
        id_name = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        function = program_ast.Function(ctx.start.line, id_name,return_type, parameters, locals, body)
        return function

    # Visit a parse tree produced by MiniParser#parameters.
    def visitParameters(self, ctx:MiniParser.ParametersContext):
        parameters = []
        for decl_ctx in ctx.decl():
            parameters.append(self.visit(decl_ctx))
        return parameters

  # Visit a parse tree produced by MiniParser#statementList.
    def visitStatementList(self, ctx:MiniParser.StatementListContext):
        statements = []
        for statement_ctx in ctx.statement():
            statements.append(self.visit(statement_ctx))
        #block_stmt = statement_ast.BlockStatement(ctx.start.line, statements)
        return statements


    
    # Visit a parse tree produced by MiniParser#IntType.
    def visitIntType(self, ctx:MiniParser.IntTypeContext):
        return type_ast.IntType()

    # Visit a parse tree produced by MiniParser#BoolType.
    def visitBoolType(self, ctx:MiniParser.BoolTypeContext):
        return type_ast.BoolType()
    
    # Visit a parse tree produced by MiniParser#StructType.
    def visitStructType(self, ctx:MiniParser.StructTypeContext):
        id_name = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        return type_ast.StructType(ctx.start.line, id_name)



    # Visit a parse tree produced by MiniParser#ReturnTypeReal.
    def visitReturnTypeReal(self, ctx:MiniParser.ReturnTypeRealContext):
        return self.visit(ctx.type_())


    # Visit a parse tree produced by MiniParser#ReturnTypeVoid.
    def visitReturnTypeVoid(self, ctx:MiniParser.ReturnTypeVoidContext):
        return type_ast.ReturnTypeVoid()


    # Visit a parse tree produced by MiniParser#NestedBlock.
    def visitNestedBlock(self, ctx:MiniParser.NestedBlockContext):
        return self.visit(ctx.block())

    # Visit a parse tree produced by MiniParser#Assignment.
    def visitAssignment(self, ctx:MiniParser.AssignmentContext):
        if ctx.expression() != None:
            source = self.visit(ctx.expression())
        else:
            source = expression_ast.ReadExpression(ctx.start.line)
        #print("CTX LVALUE", str(ctx.lvalue().__class__))
        target = self.visit(ctx.lvalue()) # visits LValueID or LValueDot as appropriate for the ctx
        #print("TARGET", target)
        assignment = statement_ast.AssignmentStatement(ctx.start.line, target, source)
        return assignment


    # Visit a parse tree produced by MiniParser#Print.
    def visitPrint(self, ctx:MiniParser.PrintContext):
        print_ = statement_ast.PrintStatement(ctx.start.line, self.visit(ctx.expression()))
        return print_


    # Visit a parse tree produced by MiniParser#PrintLn.
    def visitPrintLn(self, ctx:MiniParser.PrintLnContext):
        println = statement_ast.PrintLnStatement(ctx.start.line, self.visit(ctx.expression()))
        return println


    # Visit a parse tree produced by MiniParser#Conditional.
    def visitConditional(self, ctx:MiniParser.ConditionalContext):
        
        if ctx.elseBlock != None:
            else_block = self.visit(ctx.elseBlock)
        else:
            # Create an empty block
            else_block = statement_ast.BlockStatement(-1, [])
        conditional = statement_ast.ConditionalStatement(ctx.start.line, self.visit(ctx.expression()), self.visit(ctx.thenBlock), else_block)
        return conditional

    # Visit a parse tree produced by MiniParser#While.
    def visitWhile(self, ctx:MiniParser.WhileContext):
        while_ = statement_ast.WhileStatement(ctx.start.line, self.visit(ctx.expression()), self.visit(ctx.block()))
        return while_


    # Visit a parse tree produced by MiniParser#Delete.
    def visitDelete(self, ctx:MiniParser.DeleteContext):
        delete = statement_ast.DeleteStatement(ctx.start.line, self.visit(ctx.expression()))
        return delete


    # Visit a parse tree produced by MiniParser#Return.
    def visitReturn(self, ctx:MiniParser.ReturnContext):
        if ctx.expression() != None:
            expression = self.visit(ctx.expression())
            return_ = statement_ast.ReturnStatement(ctx.start.line, expression)
        else:
            return_ = statement_ast.ReturnEmptyStatement(ctx.start.line)
        
        return return_


    # Visit a parse tree produced by MiniParser#Invocation.
    def visitInvocation(self, ctx:MiniParser.InvocationContext):
        arguments = self.visit(ctx.arguments())
        name_id = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        invocation_expr = expression_ast.InvocationExpression(ctx.start.line, name_id, arguments)
        invocation = statement_ast.InvocationStatement(ctx.start.line, invocation_expr)
        return invocation


    # Visit a parse tree produced by MiniParser#block.
    def visitBlock(self, ctx:MiniParser.BlockContext):
        block = self.visit(ctx.statementList())
        return statement_ast.BlockStatement(ctx.start.line, block)

    # Visit a parse tree produced by MiniParser#Lvalue.
    def visitLvalueId(self, ctx:MiniParser.LvalueIdContext): # added 'Id' to context type and func name
        #if isinstance(ctx, MiniParser.LvalueIdContext):
        id_name = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        lvalue = lvalue_ast.LValueID(ctx.start.line, id_name)
        #elif isinstance(ctx, MiniParser.LvalueDotContext):
        #    lvalue = lvalue_ast.LValueDot(ctx.start.line, self._visitLValueNested(ctx.lvalue()), ctx.ID().getText())
        #else:
        #    print("WEIRD -- LValue Type unknown")
        #    lvalue = lvalue_ast.LValue(-1)
        return lvalue
    
    def visitLvalueDot(self, ctx: MiniParser.LvalueDotContext):
        name_id = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        left_value = self.visit(ctx.lvalue())
        lvaluedot = lvalue_ast.LValueDot(ctx.start.line, left_value, name_id)
        return lvaluedot

    # Visit a parse tree produced by MiniParser#IntegerExpr.
    def visitIntegerExpr(self, ctx:MiniParser.IntegerExprContext):
        integer_expr = expression_ast.IntegerExpression(ctx.start.line, ctx.INTEGER().getText())
        return integer_expr


    # Visit a parse tree produced by MiniParser#TrueExpr.
    def visitTrueExpr(self, ctx:MiniParser.TrueExprContext):
        true_expr = expression_ast.TrueExpression(ctx.start.line)
        return true_expr


    # Visit a parse tree produced by MiniParser#IdentifierExpr.
    def visitIdentifierExpr(self, ctx:MiniParser.IdentifierExprContext):
        identifier_expr = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        return identifier_expr


    # Visit a parse tree produced by MiniParser#BinaryExpr.
    def visitBinaryExpr(self, ctx:MiniParser.BinaryExprContext):
        left_expr = self.visit(ctx.lft)
        right_expr = self.visit(ctx.rht)
        binary_expr = expression_ast.BinaryExpression(ctx.op.line, ctx.op.text, left_expr, right_expr)
        return binary_expr

    # Visit a parse tree produced by MiniParser#NewExpr.
    def visitNewExpr(self, ctx:MiniParser.NewExprContext):
        name_id = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        new_expr = expression_ast.NewExpression(ctx.start.line, name_id)
        return new_expr


    # Visit a parse tree produced by MiniParser#NestedExpr.
    def visitNestedExpr(self, ctx:MiniParser.NestedExprContext):
        return self.visit(ctx.expression())


    # Visit a parse tree produced by MiniParser#DotExpr.
    def visitDotExpr(self, ctx:MiniParser.DotExprContext):
        name_id = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        dot_expr = expression_ast.DotExpression(ctx.start.line, self.visit(ctx.expression()), name_id)
        return dot_expr

    
    # Visit a parse tree produced by MiniParser#UnaryExpr.
    def visitUnaryExpr(self, ctx:MiniParser.UnaryExprContext):
        u_expr = expression_ast.UnaryExpression(ctx.start.line, ctx.op.text, self.visit(ctx.expression())) #ctx.op.text is the operator
        return u_expr

    # Visit a parse tree produced by MiniParser#InvocationExpr.
    def visitInvocationExpr(self, ctx:MiniParser.InvocationExprContext):
        name_id = expression_ast.IdentifierExpression(ctx.start.line, ctx.ID().getText())
        invocation_expr = expression_ast.InvocationExpression(ctx.start.line, name_id, self.visit(ctx.arguments()))
        return invocation_expr


    # Visit a parse tree produced by MiniParser#FalseExpr.
    def visitFalseExpr(self, ctx:MiniParser.FalseExprContext):
        false_expr = expression_ast.FalseExpression(ctx.start.line)
        return false_expr


    # Visit a parse tree produced by MiniParser#NullExpr.
    def visitNullExpr(self, ctx:MiniParser.NullExprContext):
        null_expr = expression_ast.NullExpression(ctx.start.line)
        return null_expr

    # Visit a parse tree produced by MiniParser#arguments.
    def visitArguments(self, ctx:MiniParser.ArgumentsContext):
        arguments = []
        for ectx in ctx.expression():
            arguments.append(self.visit(ectx))
        return arguments


