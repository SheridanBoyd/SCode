from rply import ParserGenerator, ParsingError
from betterast import *
from betterlexer import *

pg = ParserGenerator(
    ['OPEN_LINK', 'CLOSE_LINK', 'ALT_TEXT', 'NEW_ROOM',
     'EOL', 'CHARS', 'SCRIPT', 'NEW_SPECIAL'])


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


@pg.production('chars : CHARS')
def expression_chars(p):
    return Chars(p[0].getstr())

@pg.production('exit : exit EOL')
def expression_exit(p):
    return p[0] + '\n'

@pg.production('break : exit')
def expression_break(p):
    return Exit(p[0])


@pg.production('exit : EOL')
def expression_exit(p):
    return '\n'


@pg.production('special : NEW_SPECIAL room_desc_line EOL')
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
    return Room(p[1], Room_desc(p[3]))


@pg.production('rooms : rooms room')
def expression_rooms(p):
    return p[0] + [p[1]]


@pg.production('rooms : room')
def expression_rooms_begining(p):
    ''' room '''
    return [p[0]]


parser = pg.build()

if __name__ == '__main__':
    thing = """#start
Hi you must be new, have a *look* around and make your own game<marquee> <strong>THIS</strong> <span style='color:red'>IS</span> <em>NOT</em> <span style='background-color:#32cd32'>GOOD!!!!!!!</span></marquee>

An h1 header
============

Paragraphs are separated by a blank line.

2nd paragraph. *Italic*, **bold**, and `monospace`. Itemized lists
look like:

  * this one
  * that one
  * the other one

Note that --- not considering the asterisk --- the actual text
content starts at 4-columns in.

> Block quotes are
> written like so.
>
> They can span multiple paragraphs,
> if you like.

Use 3 dashes for an em-dash. Use 2 dashes for ranges (ex., "it's all
in chapters 12--14"). Three dots ... will be converted to an ellipsis.
Unicode is supported.



An h2 header
------------

Here's a numbered list:

 1. first item
 2. second item
 3. third item

    codeblock?
    111WWW00OOllliii

    also?

[[otherthing|alt]]
thing

![yay](https://img10.deviantart.net/89b7/i/2012/252/6/c/fluttershy__s_yay_badge_by_zutheskunk-d3e8usb.png)

"""

    tokens = lexer(thing)
    try:
        AST = parser.parse(tokens)
    except ParsingError as e:
        spos = e.getsourcepos()
        linenum = spos.lineno
        colnum = spos.colno
        raise SyntaxError('there was an error on line ' + str(linenum) + ' and column ' + str(colnum))
    print(str(AST))
    print(type(AST))
    print AST.rooms
    player = Player()
    player(AST)
