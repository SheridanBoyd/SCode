from rply import ParserGenerator, ParsingError
from betterast import *
from betterlexer import *

pg = ParserGenerator(
    ['OPEN_LINK', 'CLOSE_LINK', 'ALT_TEXT', 'NEW_ROOM',
     'EOL', 'CHARS', 'SCRIPT', 'NEW_SPECIAL', 'PRE_TAG', 'PREV_LINE'])


@pg.production('text_adventure : rooms')
def expression_text_adventure(p):
    return Text_Adventure(p)

@pg.production('script : SCRIPT')
def expression_script(p):
    return Script(p[0].getstr()[1:-1])

@pg.production('link : OPEN_LINK chars CLOSE_LINK')
def expression_link(p):
    return Link(p[1])


@pg.production('link : OPEN_LINK chars ALT_TEXT chars CLOSE_LINK')
def expression_link_alt(p):
    return Link(p[1], p[3])

@pg.production('chars : PRE_TAG')
@pg.production('chars : CHARS')
def expression_chars(p):
    return Chars(p[0].getstr())

@pg.production('chars : PREV_LINE')
def expression_chars(p):
    return Chars('')

@pg.production('exit : exit EOL')
def expression_exit(p):
    return p[0] + '\n'

@pg.production('break : exit')
def expression_break(p):
    return Exit(p[0])


@pg.production('exit : EOL')
def expression_exit(p):
    return '\n'


@pg.production('special : NEW_SPECIAL room_desc_line ')
def expression_special(p):
    return Special(p[0].getstr()[2:-1],Room_desc(p[1]))

@pg.production('room_desc_line : room_desc_line special')
@pg.production('room_desc_line : room_desc_line script')
@pg.production('room_desc_line : room_desc_line chars')
@pg.production('room_desc_line : room_desc_line link')
def expression_room_desc_line(p):
    itemlist = p[0] + [p[1]]
    return itemlist


@pg.production('room_desc_line : ')
def expression_room_desc_line(p):
    return []

#@pg.production('room_desc_line : special')
#def expression_room_desc_line(p):
#    return [p[0]]


@pg.production('room_desc : room_desc break room_desc_line ')
def expression_room_desc_begining(p):
    '''
    roomdesc: list(special/script/link/chars/break/endline)
    roomdescline: list(special/script/link/chars)
    '''
    return p[0] + [p[1]] + p[2]

@pg.production('room_desc : room_desc_line')
def expression_room_desc_begining(p):
    return p[0]

@pg.production('room : NEW_ROOM chars EOL room_desc break')
def expression_room(p):
    return Room(p[1].strip(), Room_desc(p[3]))


@pg.production('rooms : rooms room')
def expression_rooms(p):
    return p[0] + [p[1]]


@pg.production('rooms : room')
def expression_rooms_begining(p):
    ''' room '''
    return [p[0]]


parser = pg.build()

if __name__ == '__main__':
    thing = """#  start
{sellsolar = 0}
{buysolar = 1}
{sellsolar := 1}
hi
{?buysolar == 1} An entrepreneur buys your solar stuff  {buysolar := 0} {sellsolar := 0}
{?buysolar == 0} No entrepreneur's want to buy your solar stuff
hi
[[researchergame|Go back]]
"""
#     thing = """#start
# [[Design|Designing the language]]
#
# {?design == 1} [[Lexing|Lexing the language]]
#
# ~~~
# {?lexing == 1} [[Parsing|Parsing the language]]
#
# {?parsing == 1} [[AST|Making an Abstract Syntax Tree]]
# ~~~
# {?ast == 1} [[Runtime|Runtime]]
#
#
# {?runtime == 1} [[Web|Putting it on the web]]
# """

    tokens = lexer(thing)
    tokens = list(tokens)
    print(tokens)
    tokens = (t for t in tokens)
    try:
        AST = parser.parse(tokens)
    except ParsingError as e:
        spos = e.getsourcepos()
        linenum = spos.lineno
        colnum = spos.colno
        listthing = thing.split('\n')
        raise SyntaxError('there was an error on line ' + str(linenum) + ' and column ' + str(colnum) + '\n' + str(listthing[linenum]))
    print(str(AST))
    print(type(AST))
    print AST.rooms
    player = Player()
    player(AST)
