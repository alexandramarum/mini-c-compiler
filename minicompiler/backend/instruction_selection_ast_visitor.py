from miniast import mini_ast, program_ast, type_ast, statement_ast, expression_ast, lvalue_ast
from miniast.type_ast import StructType
from miniast.expression_ast import FalseExpression, TrueExpression, IntegerExpression
from static_semantic_ast_visitor import SSASTVisitor

class Frame:
    """Function frame manager."""
    WORD_SIZE = 4

    def __init__(self, name, ss_visitor=None):
        """Initialize frame with name and visitor."""
        self.name = name
        self.offsets = {} 
        self.frame_size = 0 
        self.next_param_offset = Frame.WORD_SIZE * 2
        self.next_local_offset = -Frame.WORD_SIZE
        self.ss_visitor = ss_visitor

    def allocate_param(self, param):
        """Allocate a parameter in the frame."""
        name = getattr(param, "id", param)
        offset = self.next_param_offset
        self.offsets[name] = offset
        self.next_param_offset += Frame.WORD_SIZE
        return offset

    def allocate_local(self, local):
        """Allocate a local variable in the frame."""
        name = getattr(local, "id", local)
        offset = self.next_local_offset
        self.offsets[name] = offset
        self.next_local_offset -= Frame.WORD_SIZE
        self.frame_size += Frame.WORD_SIZE
        return offset


class ISASTVisitor(mini_ast.ASTVisitor):
    """Memory-to-memory instruction selection"""
    
    def __init__(self, ss_visitor: SSASTVisitor):
        """Initialize visitor with static semantic visitor."""
        self.ss_visitor = ss_visitor
        self.struct_offsets = {}
        self.function_frames = {}
        self.current_frame = None
        self.output = []
        self.struct_vars = {}
        self.global_vars = {}
        self._label_counter = 0

    def generate_function_frames(self):
        """Generate frames for all functions."""
        for func_name, func in self.ss_visitor.function_scope.items():
            frame = Frame(func_name, ss_visitor=self.ss_visitor)
            for param in func.params:
                frame.allocate_param(param.name.id)
            for local_var in func.locals:
                frame.allocate_local(local_var.name.id)
            self.function_frames[func_name] = frame
    
    def generate_struct_offsets(self):
        """Generate field offsets for structs."""
        for type_name, type_decl in self.ss_visitor.struct_scope.items():
            offsets = {}
            current_offset = 0
            for field in type_decl.fields:
                offsets[field.name.id] = current_offset
                current_offset += Frame.WORD_SIZE
            self.struct_offsets[type_name] = offsets

    def perform_prologue(self, frame: Frame):
        """Generate function prologue: save ra, s0, and allocate stack space."""
        self.output.append(f"# prologue for {frame.name}")
        self.output.append(f"sw ra, 0(sp)")
        self.output.append(f"sw s0, 4(sp)")
        self.output.append(f"mv s0, sp")
        self.output.append(f"addi sp, sp, -{frame.frame_size}")
        self.output.append(f"# end prologue\n")

    def perform_epilogue(self, frame: Frame):
        """Generate function epilogue: restore sp, s0, ra, and return."""
        self.output.append(f"# start epilogue for {frame.name}")
        self.output.append(f"{frame.name}_epilogue:")
        self.output.append(f"addi sp, sp, {frame.frame_size}")
        self.output.append(f"lw s0, 4(sp)")
        self.output.append(f"lw ra, 0(sp)")
        if frame.name == "main":
            self.output.append(f"li a1, 0")
            self.output.append(f"li a0, 17")
            self.output.append(f"ecall")
        else:
            self.output.append(f"jr ra")
        self.output.append(f"# end epilogue for {frame.name}\n")
    
    def fresh_label(self, base="L"):
        """Generate a unique label string."""
        label = f"{base}{self._label_counter}"
        self._label_counter += 1
        return label
    
    def generate_struct_vars(self, function):
        """Identify variables that are structs to handle field access correctly."""
        self.struct_vars = {}
        for var_name, var_decl in self.global_vars.items():
            if isinstance(var_decl.type, StructType):
                self.struct_vars[var_name] = var_decl
        for param in function.params:
            if isinstance(param.type, StructType):
                self.struct_vars[param.name.id] = param.type.name.id
        for local in function.locals:
            if isinstance(local.type, StructType):
                self.struct_vars[local.name.id] = local.type.name.id

    def visit_function(self, function: program_ast.Function):
        """Visit function: setup frame, prologue, body, and epilogue."""
        frame = self.function_frames[function.name.id]
        self.current_frame = frame
        self.generate_struct_vars(function)
        
        self.output.append(f"\n{function.name.id}:")
        if function.name.id == "main":
            self.output.append("# Command Line Argument and File Setup")
            self.output.append(f"addi t0, zero, 2")
            setup_label = self.fresh_label("setup_filepath")
            skip_label = self.fresh_label("skip_filepath")
            self.output.append(f"beq a0, t0, {setup_label}")
            self.output.append(f"j {skip_label}")
            self.output.append(f"{setup_label}:")
            self.output.append("lw a0, 4(a1)")
            self.output.append("la a1, filepath_ptr")
            self.output.append("sw a0, 0(a1)")
            self.output.append(f"{skip_label}:")
        
        self.perform_prologue(frame)
        for stmt in function.body:
            self.visit_statement(stmt)
        self.perform_epilogue(frame)

    def visit_program(self, program: program_ast.Program):
        """Visit program: generate globals, text section, and visit functions."""
        self.output.append(".globl main")
        self.output.append(".import berkeley_utils.s")
        self.output.append(".import read_int.s")
        self.output.append(".data")
        for var_name, var_decl in self.ss_visitor.global_scope.items():
            self.global_vars[var_name] = var_decl
            self.output.append(f"{var_name}: .word")
        self.output.append("filepath_ptr: .word")
        self.output.append('error_string1: .asciiz "read_int returned an error\\n"')
        self.output.append('error_string2: .asciiz "incorrect number of arguments\\n"')
        self.output.append('newline: .asciiz "\\n"')
        self.output.append(".text")
        self.generate_struct_offsets()
        self.generate_function_frames()
        for func in program.functions:
            self.visit_function(func)

    def visit_statement(self, statement: statement_ast.Statement):
        """Visit a statement."""
        return statement.accept(self)
    
    def visit_assignment_statement(self, assignment_statement: statement_ast.AssignmentStatement, indent=0):
        """All assignments: result in a0, store to lvalue."""
        self.visit_expression(assignment_statement.source)  # result in a0
        self._store_to_lvalue(assignment_statement.target)  # store a0 to target

    def _store_to_lvalue(self, lvalue):
        """Store a0 to lvalue."""
        if isinstance(lvalue, lvalue_ast.LValueID):
            name = lvalue.id.id
            if name in self.global_vars:
                self.output.append(f"la t0, {name}")
                self.output.append(f"sw a0, 0(t0)")
            else:
                offset = self.current_frame.offsets[name]
                self.output.append(f"sw a0, {offset}(s0)")
        
        elif isinstance(lvalue, lvalue_ast.LValueDot):
            # Save a0 (RHS value)
            self.output.append(f"addi sp, sp, -4")
            self.output.append(f"sw a0, 0(sp)")
            
            # Load LHS struct pointer
            self._load_lvalue_address(lvalue)  # address in a0
            
            # Restore RHS value and store
            self.output.append(f"mv t0, a0")
            self.output.append(f"lw a0, 0(sp)")
            self.output.append(f"addi sp, sp, 4")
            self.output.append(f"sw a0, 0(t0)")  # store to field

    def _load_lvalue_address(self, lvalue):
        """Load address of lvalue into a0."""
        if isinstance(lvalue, lvalue_ast.LValueDot):
            # Load base struct pointer by visiting the left lvalue
            lvalue.left.accept(self)  # pointer in a0
            
            # Add field offset
            field_name = lvalue.id.id
            left_type = self._get_expression_type(lvalue.left)
            if isinstance(left_type, type_ast.StructType):
                struct_name = left_type.name.id
                offset = self.struct_offsets[struct_name][field_name]
                self.output.append(f"addi a0, a0, {offset}")

    def visit_block_statement(self, block_statement: statement_ast.BlockStatement, indent=0):
        """Visit a block of statements."""
        for stmt in block_statement.statements:
            self.visit_statement(stmt)

    def visit_conditional_statement(self, conditional_statement: statement_ast.ConditionalStatement, indent=0):
        """Visit if/else statement."""
        else_label = self.fresh_label("else")
        end_label = self.fresh_label("endif")
        self.visit_expression(conditional_statement.guard)
        self.output.append(f"beq a0, x0, {else_label}")
        self.visit_statement(conditional_statement.then_block)
        self.output.append(f"j {end_label}")
        self.output.append(f"{else_label}:")
        if conditional_statement.else_block:
            self.visit_statement(conditional_statement.else_block)
        self.output.append(f"{end_label}:")

    def visit_while_statement(self, while_statement: statement_ast.WhileStatement, indent=0):
        """Visit while loop."""
        start = self.fresh_label("while")
        end = self.fresh_label("endwhile")
        self.output.append(f"{start}:")
        self.visit_expression(while_statement.guard)
        self.output.append(f"beq a0, x0, {end}")
        self.visit_statement(while_statement.body)
        self.output.append(f"j {start}")
        self.output.append(f"{end}:")

    def visit_delete_statement(self, delete_statement: statement_ast.DeleteStatement, indent=0):
        """Delete: load pointer to a0, call free."""
        self.visit_expression(delete_statement.expression)  # pointer in a0
        # Save ra around free call
        self.output.append(f"addi sp, sp, -4")
        self.output.append(f"sw ra, 0(sp)")
        self.output.append(f"jal free")
        self.output.append(f"lw ra, 0(sp)")
        self.output.append(f"addi sp, sp, 4")

    def visit_invocation_statement(self, invocation_statement: statement_ast.InvocationStatement, indent=0):
        """Visit function call statement."""
        self.visit_invocation_expression(invocation_statement.expression)

    def visit_println_statement(self, println_statement: statement_ast.PrintLnStatement, indent=0):
        """Visit println statement: print value and newline."""
        self.visit_expression(println_statement.expression)
        self.output.append(f"mv a1, a0")
        self.output.append(f"li a0, 1")
        self.output.append("ecall")
        self.output.append(f"la a1, newline")
        self.output.append(f"li a0, 4")
        self.output.append("ecall")

    def visit_print_statement(self, print_statement: statement_ast.PrintStatement, indent=0):
        """Visit print statement: print value."""
        self.visit_expression(print_statement.expression)
        self.output.append(f"mv a1, a0")
        self.output.append(f"li a0, 1")
        self.output.append("ecall")

    def visit_return_empty_statement(self, return_empty_statement: statement_ast.ReturnEmptyStatement, indent=0):
        """Visit return void statement."""
        self.output.append(f"j {self.current_frame.name}_epilogue")

    def visit_return_statement(self, return_statement: statement_ast.ReturnStatement, indent=0):
        """Visit return value statement."""
        self.visit_expression(return_statement.expression)  # result in a0
        self.output.append(f"j {self.current_frame.name}_epilogue")

    def visit_expression(self, expression: expression_ast.Expression, indent=0):
        """Visit an expression."""
        return expression.accept(self, 0)
    
    def visit_dot_expression(self, dot_expression, indent=0):
        """Load struct.field value into a0."""
        self.visit_expression(dot_expression.left)  # struct pointer in a0
        field_name = dot_expression.id.id
        left_type = self._get_expression_type(dot_expression.left)
        if isinstance(left_type, type_ast.StructType):
            struct_name = left_type.name.id
            offset = self.struct_offsets[struct_name][field_name]
            self.output.append(f"lw a0, {offset}(a0)")

    def visit_false_expression(self, false_expression: expression_ast.FalseExpression, indent=0):
        """Visit false literal."""
        self.output.append(f"li a0, 0")

    def visit_true_expression(self, true_expression: expression_ast.TrueExpression, indent=0):
        """Visit true literal."""
        self.output.append(f"li a0, 1")

    def visit_identifier_expression(self, identifier_expression: expression_ast.IdentifierExpression, indent=0):
        """Visit identifier: load value into a0."""
        name = identifier_expression.id
        if name in self.global_vars:
            self.output.append(f"la t0, {name}")
            self.output.append(f"lw a0, 0(t0)")
        else:
            offset = self.current_frame.offsets[name]
            self.output.append(f"lw a0, {offset}(s0)")

    def visit_new_expression(self, new_expression: expression_ast.NewExpression, indent=0):
        """Allocate struct on heap, return pointer in a0."""
        struct_name = new_expression.id.id
        num_fields = len(self.struct_offsets[struct_name])
        total_size = num_fields * Frame.WORD_SIZE
        self.output.append(f"# allocate new {struct_name}")
        self.output.append(f"li a1, {total_size}")
        self.output.append(f"li a6, 1")
        self.output.append(f"li a0, 0x3CC")
        self.output.append("ecall")

    def visit_null_expression(self, null_expression: expression_ast.NullExpression, indent=0):
        """Visit null literal."""
        self.output.append(f"li a0, 0")
    
    def visit_read_expression(self, read_expression: expression_ast.ReadExpression, indent=0):
        """Read integer, return in a0."""
        # Save ra around read_int call
        self.output.append("addi sp, sp, -4")
        self.output.append("sw ra, 0(sp)")
        self.output.append("lw a0, filepath_ptr")
        self.output.append("jal ra, read_int")
        self.output.append("lw ra, 0(sp)")
        self.output.append("addi sp, sp, 4")

    def visit_integer_expression(self, integer_expression: expression_ast.IntegerExpression, indent=0):
        """Visit integer literal."""
        self.output.append(f"li a0, {integer_expression.value}")

    def visit_invocation_expression(self, invocation_expression: expression_ast.InvocationExpression, indent=0):
        """Call function, return value in a0."""
        func_name = invocation_expression.name.id
        num_args = len(invocation_expression.arguments)
        total_size = 8 + (num_args * Frame.WORD_SIZE)
        
        self.output.append(f"# start precall for {func_name}")
        self.output.append(f"addi sp, sp, -{total_size}")
        
        # Evaluate and store arguments
        for i, arg_expr in enumerate(invocation_expression.arguments):
            self.visit_expression(arg_expr)  # result in a0
            arg_offset = 8 + (i * Frame.WORD_SIZE)
            self.output.append(f"sw a0, {arg_offset}(sp)")
        
        self.output.append(f"jal ra, {func_name}")
        self.output.append(f"# end precall\n")
        
        self.output.append(f"# start postcall for {func_name}")
        self.output.append(f"addi sp, sp, {total_size}")
        self.output.append(f"# end postcall\n")
        # Return value already in a0

    def visit_unary_expression(self, unary_expression: expression_ast.UnaryExpression, indent=0):
        """Visit unary expression."""
        self.visit_expression(unary_expression.operand)
        if unary_expression.operator == expression_ast.Operator.MINUS:
            self.output.append(f"sub a0, x0, a0")
        elif unary_expression.operator == expression_ast.Operator.NOT:
            self.output.append(f"seqz a0, a0")

    def visit_binary_expression(self, binary_expression: expression_ast.BinaryExpression, indent=0):
        """Binary op: result in a0."""
        # Evaluate left
        self.visit_expression(binary_expression.left)
        # Save left
        self.output.append(f"addi sp, sp, -4")
        self.output.append(f"sw a0, 0(sp)")
        # Evaluate right
        self.visit_expression(binary_expression.right)
        # Move right to t1, reload left to a0
        self.output.append(f"mv t1, a0")
        self.output.append(f"lw a0, 0(sp)")
        self.output.append(f"addi sp, sp, 4")
        
        # Perform operation
        op = binary_expression.operator
        int_ops = {
            expression_ast.Operator.PLUS: "add",
            expression_ast.Operator.MINUS: "sub",
            expression_ast.Operator.TIMES: "mul",
            expression_ast.Operator.DIVIDE: "div"
        }
        bool_ops = {
            expression_ast.Operator.AND: "and",
            expression_ast.Operator.OR: "or"
        }
        
        if op in int_ops:
            self.output.append(f"{int_ops[op]} a0, a0, t1")
        elif op in bool_ops:
            self.output.append(f"{bool_ops[op]} a0, a0, t1")
        elif op in {expression_ast.Operator.LT, expression_ast.Operator.LE,
                    expression_ast.Operator.GT, expression_ast.Operator.GE}:
            label_true = self.fresh_label("cmp_true")
            label_end = self.fresh_label("cmp_end")
            branch_map = {
                expression_ast.Operator.LT: "blt",
                expression_ast.Operator.LE: "ble",
                expression_ast.Operator.GT: "bgt",
                expression_ast.Operator.GE: "bge"
            }
            self.output.append(f"{branch_map[op]} a0, t1, {label_true}")
            self.output.append(f"li a0, 0")
            self.output.append(f"j {label_end}")
            self.output.append(f"{label_true}:")
            self.output.append(f"li a0, 1")
            self.output.append(f"{label_end}:")
        elif op in {expression_ast.Operator.EQ, expression_ast.Operator.NE}:
            label_true = self.fresh_label("cmp_true")
            label_end = self.fresh_label("cmp_end")
            branch = "beq" if op == expression_ast.Operator.EQ else "bne"
            self.output.append(f"{branch} a0, t1, {label_true}")
            self.output.append(f"li a0, 0")
            self.output.append(f"j {label_end}")
            self.output.append(f"{label_true}:")
            self.output.append(f"li a0, 1")
            self.output.append(f"{label_end}:")

    def visit_lvalue(self, lvalue: lvalue_ast.LValue, indent=0):
        """Visit lvalue."""
        return lvalue.accept(self)

    def _get_expression_type(self, expr):
        """Get type of expression for struct field access."""
        if isinstance(expr, expression_ast.IdentifierExpression):
            name = expr.id
            if name in self.struct_vars:
                struct_type = self.struct_vars[name]
                if isinstance(struct_type, str):
                    return type_ast.StructType(linenum=0, name=type(struct_type, (), {"id": struct_type})())
                # For global variables, struct_vars contains the declaration, not the type
                if hasattr(struct_type, 'type'):
                    return struct_type.type
                return struct_type

        if isinstance(expr, lvalue_ast.LValueID):
            name = expr.id.id
            if name in self.struct_vars:
                struct_type = self.struct_vars[name]
                if isinstance(struct_type, str):
                    return type_ast.StructType(linenum=0, name=type(struct_type, (), {"id": struct_type})())
                # For global variables, struct_vars contains the declaration, not the type
                return struct_type.type if hasattr(struct_type, 'type') else struct_type

        if isinstance(expr, lvalue_ast.LValueDot):
            left_type = self._get_expression_type(expr.left)
            if isinstance(left_type, type_ast.StructType):
                struct_name = left_type.name.id
                field_name = expr.id.id
                struct_decl = self.ss_visitor.struct_scope[struct_name]
                for field in struct_decl.fields:
                    if field.name.id == field_name:
                        return field.type
        
        if isinstance(expr, expression_ast.DotExpression):
            left_type = self._get_expression_type(expr.left)
            if isinstance(left_type, type_ast.StructType):
                struct_name = left_type.name.id
                field_name = expr.id.id
                struct_decl = self.ss_visitor.struct_scope[struct_name]
                for field in struct_decl.fields:
                    if field.name.id == field_name:
                        return field.type

        if isinstance(expr, expression_ast.NewExpression):
            name = expr.id.id
            if name in self.ss_visitor.struct_scope:
                return type_ast.StructType(linenum=0, name=type(name, (), {"id": name})())

        if isinstance(expr, expression_ast.InvocationExpression):
            func_name = expr.name.id
            if func_name in self.ss_visitor.function_scope:
                return self.ss_visitor.function_scope[func_name].return_type

        return None
    
    def visit_lvalue_id(self, lvalue_id: lvalue_ast.LValueID, indent=0):
        """Visit lvalue ID: load value into a0."""
        name = lvalue_id.id.id
        if name in self.global_vars:
            self.output.append(f"la t0, {name}")
            self.output.append(f"lw a0, 0(t0)")
        else:
            offset = self.current_frame.offsets[name]
            self.output.append(f"lw a0, {offset}(s0)")

    def visit_lvalue_dot(self, lvalue_dot: lvalue_ast.LValueDot, indent=0):
        """Visit lvalue dot: load field value into a0."""
        lvalue_dot.left.accept(self)  # Load base struct pointer
        field_name = lvalue_dot.id.id
        left_type = self._get_expression_type(lvalue_dot.left)
        if isinstance(left_type, type_ast.StructType):
            struct_name = left_type.name.id
            offset = self.struct_offsets[struct_name][field_name]
            self.output.append(f"lw a0, {offset}(a0)")

    def visit_int_type(self, int_type): pass
    def visit_bool_type(self, bool_type): pass
    def visit_struct_type(self, struct_type): pass
    def visit_return_type_real(self, return_type_real): pass
    def visit_return_type_void(self, return_type_void): pass
    def visit_declaration(self, declaration): pass
    def visit_type_declaration(self, type_declaration): pass