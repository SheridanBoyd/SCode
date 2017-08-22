from .rply import LexerGenerator

lg = LexerGenerator()

lg.add('AND', r' *and *')
lg.add('NOT', r'not *')
lg.add('OR', r' *or *')
lg.add('COMP', r' *(==|!=|<=|>=|<|>) *')
lg.add('ADD', r' *\+ *')
lg.add('SUB', r' *- +')
lg.add('NEG', r'-')
lg.add('MUL', r' *\* *')
lg.add('DIV', r' *\/ *')
lg.add('EXP', r' *\^ *')
lg.add('DEF', r' *= *')
lg.add('EQ', r' *:= *')

lg.ignore(r';;.*')  # Captures Comments

lg.add('LB', r'\( *')
lg.add('RB', r' *\)')
lg.add('LLB', r'\[ *')
lg.add('LRB', r' *\]')
lg.add('COM', r' *, *')
lg.add('NL', r'[\n\r;]+')

lg.add('NXT', r'next +')
lg.add('NXV', r'_')

lg.add('GPH', r'graph +')

lg.add('TRC', r'trace +')

lg.add('STRING', r'"[^"]*"')
lg.add('NUMBER', r'\d+(\.\d+)?(e[\-\+]\d{1,3})?')
lg.add('IDENT', r'[a-zA-Z][a-zA-Z0-9]*(\-[a-zA-Z0-9]+)?')
lg.add('SPC', r' +')


lexer = lg.build()

if __name__ == '__main__':
    from zscript.rply import *
    test = """a := 1;b := 2;c := 1;d2 = b^2 - 4*a*c;x1 = -b + d2^0.5;x2 = -b - d2^0.5;[a, b, c, d2, x1, x2];"""
    # for token in lexer.lex(test):
    #     print token

    #test = """a 1 1.0 := = A + A -A * A / A ^ A ; ( ) [ A A A A A A ] , != A ?= A <= A >= A < A > next _ a_ trace "aliuhv h289f42 R #$@#T 4321r " "" """
    expected = [Token('IDENT', 'a'), Token('IDENT', 'A'), Token('NUMBER', '1'), Token('NUMBER', '1.0'),
                Token('EQ', ':='), Token('DEF', '='), Token('ADD', '+'), Token('SUB', '-'),
                Token('MUL', '*'), Token('DIV', '/'), Token('EXP', '^'), Token('NL', ';'),
                Token('LB', '('), Token('RB', ')'), Token('LLB', '['), Token('LRB', ']'),
                Token('SEP', ','), Token('COMP', '!='), Token('COMP', '?='), Token('COMP', '<='),
                Token('COMP', '>='), Token('COMP', '<'), Token('COMP', '>'), Token('NXT', 'next'), Token('NXV', '_'),
                Token('IDENT', 'a'), Token('NXV', '_'), Token('TRC', 'trace'), Token('STRING', '"aliuhv h289f42 R #$@#T 4321r "'),
                Token('STRING', '""')]
    n = []
    x = 0
    for t in expected:
        n.append(t)
        x += len(t.getstr())
        # s = ''
        # while x<len(test) and test[x] == ' ':
        #     s+=' '
        #     x+=1
        # if s:
        #     n.append(Token('SPACE', s))

    t = []
    try:
        print(list(lexer.lex(test)))
    except Exception as e:
        l = e.source_pos.lineno
        c = e.source_pos.idx
        raise Exception('error, %d, %d' %(l,c))
    for token, exp in zip(lexer.lex(test), n):
        v = token == exp
        t.append(v)
        print(v, token, exp, token.getstr()[1:-1] if token.gettokentype() == 'STRING' else token.getstr())
    print('Lexer Works', sum(t) == len(t))