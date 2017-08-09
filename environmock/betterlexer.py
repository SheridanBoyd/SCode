from rply import LexerGenerator

lg = LexerGenerator()

lg.add('OPEN_LINK', r'\[\[')
lg.add('CLOSE_LINK', r'\]\]')
lg.add('ALT_TEXT', r'\|')
lg.add('NEW_ROOM', r'#')
lg.add('NEW_SPECIAL', r'{\?[ -\|]*}')
lg.add('SCRIPT', r'{[ -\|]*}')
lg.add('EOL', r'\n')
lg.add('CHARS', r'[ -~]+')

l = lg.build()

def lexer(text):
    text += '\n\n\n'
    return l.lex(text)

if __name__=='__main__':
    thing = """#brief
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
    print(tokens)