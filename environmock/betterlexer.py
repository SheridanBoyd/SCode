from rply import LexerGenerator

lg = LexerGenerator()

lg.add('OPEN_LINK', r'\[\[')
lg.add('CLOSE_LINK', r'\]\]')
lg.add('ALT_TEXT', r'\|')
lg.add('NEW_ROOM', r'#')
lg.add('NEW_SPECIAL', r'{\?[ -\|]*}')
lg.add('SCRIPT', r'{[ -\|]*}')
lg.add('EOL', r'\n|\r|\r\n')
lg.add('CHARS', r'[^\]\[\{\}\|\n|\r|\r\n]+')

l = lg.build()

def lexer(text):
    text += '\n\n\n'
    return l.lex(text)

if __name__=='__main__':
    thing = """#start
[[test]] {blah = 0} [[blah]]

#test
this is a test [[blah]] {blah = 1}

#blah
{?blah ?= 1} hello this is working
[[start]]

"""
    tokens = lexer(thing)
    print(list(tokens)[1].getstr())