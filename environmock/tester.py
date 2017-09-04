from rply import ParserGenerator, ParsingError
from betterast import *
from betterlexer import *

pg = ParserGenerator(
    ['OPEN_LINK', 'CLOSE_LINK', 'ALT_TEXT', 'NEW_ROOM',
     'END_LINE', 'EXIT', 'CHARS'])
game = '''#################'''

print(str('hi'))
