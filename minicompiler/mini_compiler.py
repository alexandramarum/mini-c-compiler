import sys
from antlr4 import *
from MiniLexer import MiniLexer
from MiniParser import MiniParser
from mini_ast_visitor import MiniToASTVisitor
from pretty_print_ast_visitor import PPASTVisitor
from static_semantic_ast_visitor import SSASTVisitor
from instruction_selection_ast_visitor import ISASTVisitor
import argparse

def main(argv):
    parser = argparse.ArgumentParser(
        description="Mini Compiler"
    )

    parser.add_argument(
        "-p", "--pretty", action="store_true",
        help="Pretty-print the AST."
    )

    parser.add_argument(
        "filename",
        help="Mini source file to compile (e.g., test123.mini)"
    )

    args = parser.parse_args(argv[1:])
        
    input_stream = FileStream(args.filename)  # create a stream of characters from the input file (e.g., test.mini)
    lexer = MiniLexer(input_stream)     # create a lexer for the input stream
    stream = CommonTokenStream(lexer)   
    parser = MiniParser(stream)         # create a parser for the stream of tokens
    program_ctx = parser.program()      # recursively parse, starting with the top-level 'program' construct of Mini.g4

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax errors.")
    else:
        print("Parse successful.")
        """Create AST."""
        mini_ast_visitor = MiniToASTVisitor()
        mini_ast = mini_ast_visitor.visitProgram(program_ctx)
        print("AST created.")
        print(mini_ast)

        if args.pretty:
            """Pretty print AST.
            Milestone 0: Implement this visitor"""
            pp_visitor = PPASTVisitor()
            pp_str = mini_ast.accept(pp_visitor)
            print(pp_str)

        # --- Static Semantic Analysis ---
        ss_visitor = SSASTVisitor()
        mini_ast.accept(ss_visitor)

        if ss_visitor.total_errors > 0:
            print(f"Static semantic analysis found {ss_visitor.total_errors} errors. Compilation stopped.")
            return  # Stop compilation before instruction selection

        print("Static semantic analysis passed. Proceeding to code generation.")

        # --- Instruction Selection (Milestone 2) ---
        is_visitor = ISASTVisitor(ss_visitor)
        mini_ast.accept(is_visitor)

        # Extract assembly text (list → string if necessary)
        if isinstance(is_visitor.output, list):
            assembly_text = "\n".join(is_visitor.output)
        else:
            assembly_text = is_visitor.output

        # Determine output file name
        input_filename = args.filename
        if input_filename.endswith(".mini"):
            output_filename = input_filename[:-5] + ".s"
        else:
            output_filename = input_filename + ".s"

        # Write to .s file
        with open(output_filename, "w") as f:
            f.write(assembly_text)

        print(f"Assembly written to {output_filename}")



if __name__ == '__main__':
    main(sys.argv)


