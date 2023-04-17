import argparse
import pathlib
import sys
import ply.lex as lex

class UCLexer:
    """A lexer for the uC language. After building it, set the
    input text with input(), and call token() to get new
    tokens.
    """

    def __init__(self, error_func):
        """Create a new Lexer.
        An error function. Will be called with an error
        message, line and column as arguments, in case of
        an error during lexing.
        """
        self.error_func = error_func
        self.filename = ""

        # Keeps track of the last token returned from self.token()
        self.last_token = None

    def build(self, **kwargs):
        """Builds the lexer from the specification. Must be
        called after the lexer object is created.
        This method exists separately, because the PLY
        manual warns against calling lex.lex inside __init__
        """
        self.lexer = lex.lex(object=self, **kwargs)

    def reset_lineno(self):
        """Resets the internal line number counter of the lexer."""
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    def find_tok_column(self, token):
        """Find the column of the token in its line."""
        last_cr = self.lexer.lexdata.rfind("\n", 0, token.lexpos)
        return token.lexpos - last_cr

    # Internal auxiliary methods
    def _error(self, msg, token):
        location = self._make_tok_location(token)
        self.error_func(msg, location[0], location[1])
        self.lexer.skip(1)

    def _make_tok_location(self, token):
        return (token.lineno, self.find_tok_column(token))

    # Reserved keywords
    keywords = (
        "ASSERT",
        "BREAK",
        "CHAR",
        "ELSE",
        "FOR",
        "IF",
        "INT",
        "PRINT",
        "READ",
        "RETURN",
        "VOID",
        "WHILE",
    )

    keyword_map = {}
    for keyword in keywords:
        keyword_map[keyword.lower()] = keyword

    #
    # All the tokens recognized by the lexer
    #
    tokens = keywords + (
        # Identifiers
        "ID",
        # constants
        "INT_CONST",
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "LPAREN",
        "RPAREN",
        "LBRACE",
        "RBRACE",
        "SEMI",
        "EQUALS",
        "EQ",
        "COMMA",
        "STRING_LITERAL",
        "NE",
        "MOD",
        "GT",
        "NOT",
        "LT",
        "GE",
        "LE",
        "LBRACKET",
        "RBRACKET",
        "CHAR_CONST",
        "AND",
        "OR"
    )
      
    #
    # Rules
    #
    t_ignore = " \t"
    # Newlines
    def t_NEWLINE(self, t):
        # include a regex here for newline
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_ID(self, t):
        # include a regex here for ID
        r'[a-zA-Z_][0-9a-zA-Z_]*'
        t.type = self.keyword_map.get(t.value, "ID")
        return t
    
    def t_TIMES(self, t):
        # include a regex here for times
        r'[\*]'
        t.type = self.keyword_map.get(t.value, "TIMES")
        return t

    def t_comma(self, t):
        # include a regex here for comma
        r'\,'
        t.type = self.keyword_map.get(t.value, "COMMA")
        return t
    
    def t_comment(self, t):
        # include a regex here for comment 
        r'(/\*(.|\n)*?\*/)|(//.*)'
        t.lexer.lineno += t.value.count("\n")
        pass

    def t_comment_unterminated(self, t):
        r'(/\*(.|\n)*)'
        msg = "Unterminated comment"
        self._error(msg, t)

    def t_string_literal(self, t):
        # include a regex here for string_literal
        r'\"(\\.|[^"\\])*\"'
        t.value = t.value.replace("\"","")
        t.type = self.keyword_map.get(t.value, "STRING_LITERAL")
        return t
    
    def t_ne(self, t):
        # include a regex here for ne
        r'!='
        t.type = self.keyword_map.get(t.value, "NE")
        return t
        
    def t_mod(self, t):
        # include a regex here for mod
        r'%'
        t.type = self.keyword_map.get(t.value, "MOD")
        return t

    def t_divide(self, t):
        # include a regex here for mod
        r'/'
        t.type = self.keyword_map.get(t.value, "DIVIDE")
        return t

    def t_char_const(self, t):
        # include a regex here for char_const
        r'(L)?\'([^\\\n]|(\\.))*?\''
        t.type = self.keyword_map.get(t.value, "CHAR_CONST")
        return t 
        
    def t_not(self, t):
        # include a regex here for not
        r'!'
        t.type = self.keyword_map.get(t.value, "NOT")
        return t
    
    def t_gt(self, t):
        # include a regex here for gt
        r'>(?=[^=])'
        t.type = self.keyword_map.get(t.value, "GT")
        return t    
    
    def t_ge(self, t):
        # include a regex here for ge
        r'(?<!>=)>=(?!>=)'
        t.type = self.keyword_map.get(t.value, "GE")
        return t 
    
    def t_lt(self, t):
        # include a regex here for lt
        r'<(?=[^=])'
        t.type = self.keyword_map.get(t.value, "LT")
        return t

    def t_and(self, t):
        # include a regex here for and
        r'&&'
        t.type = self.keyword_map.get(t.value, "AND")
        return t
        
    def t_or(self, t):
        # include a regex here for or
        r'\|\|'
        t.type = self.keyword_map.get(t.value, "OR")
        return t

    def t_le(self, t):
        # include a regex here for le
        r'(?<!<=)<=(?!<=)'
        t.type = self.keyword_map.get(t.value, "LE")
        return t 

    def t_lbracket(self, t):
        # include a regex here for lbracket
        r'\['
        t.type = self.keyword_map.get(t.value, "LBRACKET")
        return t 

    def t_rbracket(self, t):
        # include a regex here for rbracket
        r'\]'
        t.type = self.keyword_map.get(t.value, "RBRACKET")
        return t

    def t_plus(self, t):
        # include a regex here for plus
        r'\+'
        t.type = self.keyword_map.get(t.value, "PLUS")
        return t
        pass

    def t_minus(self, t):
        # include a regex here for minus
        r'-'
        t.type = self.keyword_map.get(t.value, "MINUS")
        return t

    def t_lparen(self, t):
        # include a regex here for lparen
        r'\('
        t.type = self.keyword_map.get(t.value, "LPAREN")
        return t

    def t_rparen(self, t):
        # include a regex here for rparen
        r'\)'
        t.type = self.keyword_map.get(t.value, "RPAREN")
        return t

    def t_lbrace(self, t):
        # include a regex here for lbrace
        r'\{'
        t.type = self.keyword_map.get(t.value, "LBRACE")
        return t

    def t_rbrace(self, t):
        # include a regex here for rbrace
        r'\}'
        t.type = self.keyword_map.get(t.value, "RBRACE")
        return t
    
    def t_semi(self, t):
        # include a regex here for semi
        r';'
        t.type = self.keyword_map.get(t.value, "SEMI")
        return t
   
    def t_equals(self, t):
        # include a regex here for equals
        r'(?<!=)=(?!=)'
        t.type = self.keyword_map.get(t.value, "EQUALS")
        return t

    def t_eq(self, t):
        # include a regex here for equals
        r'(?<!=)==(?!=)'
        t.type = self.keyword_map.get(t.value, "EQ")
        return t    
    
    def t_int_const(self, t):
        # include a regex here for int_const
        r'[0-9]+'
        t.type = self.keyword_map.get(t.value, "INT_CONST")
        return t
   
    def t_error(self, t):
        msg = "Illegal character %s" % repr(t.value[0])
        self._error(msg, t)

    # Scanner (used only for test)
    def scan(self, data):
        self.lexer.input(data)
        output = ""
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
            output += str(tok) + "\n"
        return output


if __name__ == "__main__":

    # create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to file to be scanned", type=str)
    args = parser.parse_args()

    # get input path
    input_file = args.input_file
    input_path = pathlib.Path(input_file)

    # check if file exists
    if not input_path.exists():
        print("Input", input_path, "not found", file=sys.stderr)
        sys.exit(1)

    def print_error(msg, x, y):
        # use stdout to match with the output in the .out test files
        print("Lexical error: %s at %d:%d" % (msg, x, y), file=sys.stdout)

    # set error function
    m = UCLexer(print_error)
    # Build the lexer
    m.build()
    # open file and print tokens
    with open(input_path) as f:
        m.scan(f.read())