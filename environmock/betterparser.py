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
    return p[0].getstr()

@pg.production('exit : exit EOF')
def expression_exit(p):
    return p[0] + '\n'

@pg.production('break : exit')
def expression_break(p):
    return Exit(p[0])


@pg.production('end_line : EOF')
def expression_end_line(p):
    return Endline()


@pg.production('exit : EOF')
def expression_exit(p):
    return '\n'


@pg.production('special : NEW_SPECIAL room_desc_line EOF')
def expression_special(p):
    return Special(p[0].getstr()[2:-1],p[1])


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


@pg.production('room_desc : room_desc_line room_desc')
def expression_room_desc_begining(p):
    return p[0] + p[1]


@pg.production('room_desc : room_desc break room_desc_line ')
def expression_room_desc_begining(p):
    return p[0] + p[2]


@pg.production('room : NEW_ROOM chars EOL room_desc break')
def expression_room(p):
    return Room(p[1], Room_desc(p[3]))


@pg.production('rooms : rooms room')
def expression_rooms(p):
    return p[0] + [p[1]]


@pg.production('rooms : room')
def expression_rooms_begining(p):
    return [p[0]]


parser = pg.build()

if __name__ == '__main__':
    thing = """#start
[[briefsge|Brief for Sheridan Game Engine]]
[[briefccg|Brief for Climate Change Game]]
Why am I using my website instead of twine?
because my website is server side meaning that it can be played by multiple people.
The importance of games being able to be played by multiple people is that it can be cooperative.
The importance of it being cooperative is that in the real world, people have to cooperate to solve climate change.
One person can't fix climate change by themselves. So in my climate change game, I want multiple players so that people have to cooperate to win and it means they know what it's like in real life with how countries have to cooperate. It is also good in a class room environment because it means that classmates can work and learn together on the game. The reason that I'm not using Twine is because Twine is client side, meaning it's all run through the player's end and the different players can't play together.
Another reason why I'm using my own program instead of Twine is because I can change my program to fit the needs of my game, so that my game is exactly how I want it.
I want this to be used by...
Game engine for those who want to make games that aren't professional programmers. And those who want to collaborate on the project.
Note taking program for those who want to take notes collaboratively.
[[start]]




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
