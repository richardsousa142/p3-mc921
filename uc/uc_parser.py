import argparse
import pathlib
import sys
from ply.yacc import yacc
from uc.uc_ast import (
    ID,
    ArrayDecl,
    ArrayRef,
    Assert,
    Assignment,
    BinaryOp,
    Break,
    Compound,
    Constant,
    Decl,
    DeclList,
    EmptyStatement,
    ExprList,
    For,
    FuncCall,
    FuncDecl,
    FuncDef,
    GlobalDecl,
    If,
    InitList,
    ParamList,
    Print,
    Program,
    Read,
    Return,
    Type,
    UnaryOp,
    VarDecl,
    While,
)
from uc.uc_lexer import UCLexer


class Coord:
    """Coordinates of a syntactic element. Consists of:
    - Line number
    - (optional) column number, for the Lexer
    """

    __slots__ = ("line", "column")

    def __init__(self, line, column=None):
        self.line = line
        self.column = column

    def __str__(self):
        if self.line and self.column is not None:
            coord_str = "@ %s:%s" % (self.line, self.column)
        elif self.line:
            coord_str = "@ %s" % (self.line)
        else:
            coord_str = ""
        return coord_str


class UCParser:
    def __init__(self, debug=True):
        """Create a new uCParser."""
        self.uclex = UCLexer(self._lexer_error)
        self.uclex.build()
        self.tokens = self.uclex.tokens

        self.ucparser = yacc(module=self, start="program", debug=debug)
        # Keeps track of the last token given to yacc (the lookahead token)
        self._last_yielded_token = None

    def parse(self, text, debuglevel=0):
        self.uclex.reset_lineno()
        self._last_yielded_token = None
        return self.ucparser.parse(input=text, lexer=self.uclex, debug=debuglevel)

    def _lexer_error(self, msg, line, column):
        # use stdout to match with the output in the .out test files
        print("LexerError: %s at %d:%d" % (msg, line, column), file=sys.stdout)
        sys.exit(1)

    def _parser_error(self, msg, coord=None):
        # use stdout to match with the output in the .out test files
        if coord is None:
            print("ParserError: %s" % (msg), file=sys.stdout)
        else:
            print("ParserError: %s %s" % (msg, coord), file=sys.stdout)
        sys.exit(1)

    def _token_coord(self, p, token_idx):
        last_cr = p.lexer.lexer.lexdata.rfind("\n", 0, p.lexpos(token_idx))
        if last_cr < 0:
            last_cr = -1
        column = p.lexpos(token_idx) - (last_cr)
        return Coord(p.lineno(token_idx), column)

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NE'),
        ('left', 'GT', 'GE', 'LT', 'LE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD')
    )

    def p_program(self, p):
            """program : global_declaration_list"""
            p[0] = ('Program', p[1])

    def p_global_declaration_list(self, p):
        """global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_global_declaration(self, p):
        """global_declaration : function_definition
                                | declaration
        """
        
        pass

    def p_function_definition(self, p):
        """function_definition : type_specifier declarator compound_statement
                                | type_specifier declarator declaration_list compound_statement
        """
        pass

    #feito (funciona ?)
    def p_type_specifier(self, p):
        """type_specifier : VOID
                          | CHAR
                          | INT
        """
        p[0] = Type([p[1]], coord=self._token_coord(p, 1))
        #pass

    def p_declarator(self, p):
        """declarator : identifier
                      | LPAREN declarator RPAREN
                      | declarator LBRACKET RBRACKET
                      | declarator LBRACKET constant_expression RBRACKET
                      | declarator LPAREN RPAREN
                      | declarator LPAREN parameter_list RPAREN
        """
        pass

    def p_constant_expression(self, p):
        """constant_expression : binary_expression
        """
        pass
    
    #feito (funciona ?)
    def p_binary_expression(self, p):
        """binary_expression : unary_expression
                                | binary_expression TIMES binary_expression
                                | binary_expression DIVIDE binary_expression
                                | binary_expression MOD binary_expression
                                | binary_expression PLUS binary_expression
                                | binary_expression MINUS binary_expression
                                | binary_expression LT binary_expression
                                | binary_expression LE binary_expression
                                | binary_expression GT binary_expression
                                | binary_expression GE binary_expression
                                | binary_expression EQ binary_expression
                                | binary_expression NE binary_expression
                                | binary_expression AND binary_expression
                                | binary_expression OR binary_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)
        pass

    def p_unary_expression(self, p):
        """unary_expression : postfix_expression
                            | unary_operator unary_expression
        """
        pass
    
    #feito (funciona ?)
    def p_postfix_expression(self, p): #1,2,3
        """postfix_expression : primary_expression
                              | postfix_expression LBRACKET expression RBRACKET
                              | postfix_expression LPAREN RPAREN
                              | postfix_expression LPAREN argument_expression RPAREN
        """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 5 and p[2] == 'LBRACKET':
            p[0] = ArrayRef(p[1], p[3], p[1].coord)
        else:
            p[0] = FuncCall(p[1], p[3] if len(p) == 5 else None, p[1].coord)
        #pass

    def p_primary_expression(self, p):
        """primary_expression : identifier
                              | constant
                              | STRING_LITERAL
                              | LPAREN expression RPAREN
        """
        pass
    
    #feito (funciona ?)
    def p_constant(self, p):
        """constant : INT_CONST
                    | CHAR_CONST
        """
        if p[1] == "INT_CONST":
            type = "int"
        else:
            type = "char"
        p[0] = Constant(type, p[1], self._token_coord(p, 1))
        #pass

    #feito (funciona ?)
    def p_expression(self, p):
        """expression : assignment_expression
                      | expression COMMA assignment_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1], ExprList):
                p[1] = ExprList([p[1]], p[1].coord)

            p[1].exprs.append(p[3])
            p[0] = p[1]
        #pass

    #feito (funciona ?)
    def p_argument_expression(self, p):
        """argument_expression : assignment_expression
                               | argument_expression COMMA assignment_expression
        """
        if len(p) == 2:
            p[0] = ExprList([p[1]], p[1].coord)
        else:
            p[1].exprs.append(p[3])
            p[0] = p[1]
        #pass

    #feito (funciona ?)
    def p_assignment_expression(self, p):
        """assignment_expression : binary_expression
                                 | unary_expression EQUALS assignment_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Assignment(p[2], p[1], p[3], p[1].coord)
        #pass

    def p_unary_operator(self, p):
        """unary_operator : PLUS
                          | MINUS
                          | NOT
        """
        pass

    #feito (funciona ?)
    def p_parameter_list(self, p):
        """parameter_list : parameter_declaration
                          | parameter_list COMMA parameter_declaration
        """
        if len(p) == 2:
            p[0] = ParamList([p[1]], p[1].coord)
        else:
            p[1].params.append(p[3])
            p[0] = p[1]
        #pass

    def p_parameter_declaration(self, p):
        """parameter_declaration : type_specifier declarator
        """
        pass

    def p_declaration(self, p):
        """declaration : type_specifier SEMI
                       | type_specifier init_declarator_list SEMI
        """
        pass

    def p_declaration_list(self, p):
        """declaration_list : declaration
                            | declaration_list declaration
        """
        pass

    def p_init_declarator_list(self, p):
        """init_declarator_list : init_declarator
                                | init_declarator_list COMMA init_declarator
        """
        pass

    def p_init_declarator(self, p):
        """init_declarator : declarator
                            | declarator EQUALS initializer
        """
        pass
    
    #feito (funciona ?)
    def p_initializer(self, p):
        """initializer : assignment_expression
                       | LBRACE RBRACE
                       | LBRACE initializer_list RBRACE
                       | LBRACE initializer_list COMMA RBRACE
        """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = p[1] + p[2]
        elif (p[2] is None) and (len(p) == 4):
            p[0] = InitList([], self._token_coord(p, 1))
        else:
            p[0] = p[2]
        #pass

    def p_initializer_list(self, p):
        """initializer_list : initializer
                            | initializer_list COMMA initializer
        """
        pass

    def p_compound_statement(self, p):
        """compound_statement : LBRACE RBRACE
                              | LBRACE declaration_list RBRACE
                              | LBRACE statement_list RBRACE
                              | LBRACE declaration_list statement_list RBRACE
        """
        pass
    
    #feito (funciona ?)
    def p_statement(self, p):
        """statement : expression_statement
                     | compound_statement
                     | selection_statement
                     | iteration_statement
                     | jump_statement
                     | assert_statement
                     | print_statement
                     | read_statement
        """
        pass

    def p_statement_list(self, p):
        """statement_list : statement
                          | statement_list statement
        """
        pass
    
    #feito (funciona ?)
    def p_expression_statement(self, p):
        """expression_statement : SEMI
                                | expression SEMI
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            if p[1] is None:
                p[0] = EmptyStatement(self._token_coord(p, 2))
            else:
                p[0] = p[1]
        #pass
    
    #feito (funciona ?)
    def p_selection_statement(self, p):
        """selection_statement : IF LPAREN expression RPAREN statement
                               | IF LPAREN expression RPAREN statement ELSE statement
        """
        if len(p) == 6:
            p[0] = If(p[3], p[5], None, self._token_coord(p, 1))
        else:
            p[0] = If(p[3], p[5], p[7], self._token_coord(p, 1))
        #pass

    def p_iteration_statement(self, p):
        """iteration_statement : WHILE LPAREN expression RPAREN statement
                               | FOR LPAREN SEMI SEMI RPAREN statement
                               | FOR LPAREN expression SEMI SEMI RPAREN statement
                               | FOR LPAREN SEMI expression SEMI RPAREN statement
                               | FOR LPAREN SEMI SEMI expression RPAREN statement
                               | FOR LPAREN expression SEMI expression SEMI RPAREN statement
                               | FOR LPAREN expression SEMI SEMI expression RPAREN statement
                               | FOR LPAREN SEMI expression SEMI expression RPAREN statement
                               | FOR LPAREN expression SEMI expression SEMI expression RPAREN statement
                               | FOR LPAREN declaration SEMI RPAREN statement
                               | FOR LPAREN declaration expression SEMI RPAREN statement
                               | FOR LPAREN declaration SEMI expression RPAREN statement
                               | FOR LPAREN declaration expression SEMI expression RPAREN statement
        """
        if p[1] == "WHILE":
            p[0] = While(p[3], p[5], self._token_coord(p, 1))
        elif
        #pass

    def p_jump_statement(self, p):
        """jump_statement : BREAK SEMI
                            | RETURN SEMI
                            | RETURN expression SEMI
        """
        pass

    def p_assert_statement(self, p):
        """assert_statement : ASSERT expression SEMI
        """
        pass

    def p_print_statement(self, p):
        """print_statement : PRINT LPAREN RPAREN SEMI
                            | PRINT LPAREN expression RPAREN SEMI
        """
        pass

    def p_read_statement(self, p):
        """read_statement : READ LPAREN argument_expression RPAREN SEMI
        """
        pass

    def p_identifier(self, p):
        """identifier : ID"""
        p[0] = ('ID', p[1])
        p.set_lineno(0, p.lineno(1))

    def p_error(self, p):
        if p:
            self._parser_error(
                "Before %s" % p.value, Coord(p.lineno, self.uclex.find_tok_column(p))
            )
        else:
            self._parser_error("At the end of input (%s)" % self.uclex.filename)


if __name__ == "__main__":

    # create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to file to be parsed", type=str)
    args = parser.parse_args()

    # get input path
    input_file = args.input_file
    input_path = pathlib.Path(input_file)

    # check if file exists
    if not input_path.exists():
        print("ERROR: Input", input_path, "not found", file=sys.stderr)
        sys.exit(1)

    def print_error(msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y), file=sys.stderr)

    # set error function
    p = UCParser()
    # open file and print ast
    with open(input_path) as f:
        ast = p.parse(f.read())
        ast.show(buf=sys.stdout, showcoord=True)
