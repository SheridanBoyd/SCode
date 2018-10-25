#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
try:
    import webapp2
except:
    pass

#import zscript.zscript as zs
from betterdatabase import *

import zscript as zs
import lexerparser
import betterlexer as bl
import betterparser as bp
#from markdown import markdown
import markdown
import betterast as ba

textadventure = None #IT gets set later in gamehandler and gets used
zenvironment = zs.Env(repl=True)
environment = {'zenvironment':zenvironment}
md = markdown.Markdown(extensions=['markdown.extensions.fenced_code','markdown.extensions.nl2br','urlize'])


example = """#start
[[music]]

#music
The music room has a grand piano on a low stage in one corner. There is a music stand with a sheet of notes. Do you want to [[play]] the music?

#play
You hear the [[opening]] of Beethoven's Fifth Symphony 

#opening
A secret door hidden behind a large tapestry opens to a stairwell going [[down]]. 

#down
You follow the staircase down down down until you get to a [[music|music room]]

"""

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("""<form action="/token" method="post">
  Username:<br>
  <input type="text" name="username" value="johndoe45"><br>
  Password:<br>
  <input type="password" name="password" value="Ilovecats"><br><br>
  <input type="submit" value="Submit">
</form>""")

class InventoryHandler(webapp2.RequestHandler):
    def get(self,it):
        self.response.write("""<h1>Inventory</h1>

%s has:<br>
a lamp<br>
a disease<br>
a meat<br>
a water<br>
edit the <a href="/%s/editing">game?</a>
""" % (it,it))
   
class TokenHandler(webapp2.RequestHandler):
    def post(self):
        global environment
        password = str(self.request.get('password'))
        username = str(self.request.get('username'))
        token = username+password+'12'
        query = User.query(User.token == token)
        user = query.get()
        environment['token'] = token
        if user == None:
            user = User()
            user.token = token
            user.game = """#start
Hi you must be new, have a look around and make your own game

"""
            user.put()
        self.response.write("""Hi %s!<br>This is your <a href="/%s/quickedit">token</a>""" % (username,token))

class QuickEditHandler(webapp2.RequestHandler):
    def get(self,token):
        global textadventure
        query = User.query(User.token == token)
        user = query.get()
        try:
            lexedstring = bl.lexer(user.game)
        except lexerparser.LexingError as e:
            game = """#start
            Oh nooos, something went wrong!
            {e}
            """.format(e=e)
            lexedstring = bl.lexer(game)
        try:
            textadventure = bp.parser.parse(lexedstring)
        except lexerparser.ParsingError as e:
            game = """#start
            Oh nooos, something went wrong!
            {e}
            """.format(e = e)
            lexedstring = bl.lexer(game)
            textadventure = bp.parser.parse(lexedstring)
        self.response.write("""<frameset cols="50%,50%">
  <frame src="/{token}/rooms/start" name='game'>
  <frame src="/{token}/editing" name='misc'>
</frameset>""".format(token = token))


class GameHandler(webapp2.RequestHandler):
    def get(self,token):
        self.response.write("<div id='game'></div>")

class RoomHandler(webapp2.RequestHandler):
    def get(self,token,room):
        global environment
        global textadventure
        query = User.query(User.token == token)
        user = query.get()
        game = user.game
        lexedstring = bl.lexer(game)
        textadventure = bp.parser.parse(lexedstring)
        environment['token'] = token
        self.response.write(md.convert(((textadventure.rooms[room]).htmlstr(environment))))

class EditingHandler(webapp2.RequestHandler):
    def get(self,token):
        message = str(self.request.get('message'))
        game = str(self.request.get('game'))
        query = User.query(User.token == token)
        user = query.get()
        if game == '':
            game = user.game
        self.response.write("""{message}<form action="/{token}/savegame" method="post">
  Game:<br><textarea name="game" rows="50" cols="100">{game}</textarea><br>
  <input type="submit" value="Save">

</form>""".format(token = token,message = message, game = game))

class SaveHandler(webapp2.RequestHandler):
    def post(self,token):
        global textadventure
        game = self.request.get('game')
        game = str(game.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2028", "\n"))
        try:
            lexedstring = bl.lexer(game)
        except bl.LexingError as e:
            uri = self.uri_for('editing', token=token, message='something went wrong with lexing {e}'.format(e=str(e)), game=game )
            self.redirect(uri)
        else:
            try:
                textadventure = bp.parser.parse(lexedstring)
            except bp.ParsingError as e:
                spos = e.getsourcepos()
                linenum = spos.lineno
                colnum = spos.colno
                listthing = game.split('\n')

                raise SyntaxError('there was an error on line ' + str(linenum) + ' and column ' + str(colnum) + '\n' + str(listthing[linenum-2]) + '\n' + str(listthing[linenum-1]) + '\n' + str(listthing[linenum]))
        query = User.query(User.token == token)
        user = query.get()
        user.game = game
        user.put()
        self.response.write("""Your game is now <a href="/{token}/rooms/start" target='game'>playable</a><br>Go back to <a href="/{token}/editing">editing</a>""".format(token = token))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/([\w\d\.\-]+)/inventory', InventoryHandler),
    ('/token', TokenHandler),
    ('/([\w\d\.\-]+)/quickedit', QuickEditHandler),
    ('/([\w\d\.\-]+)/rooms/([\w\d\.\-]+)', RoomHandler),
#   ('/([a-zA-Z0-9]+)/editing', EditingHandler),
    ('/([\w\d\.\-]+)/game', GameHandler),
    ('/([\w\d\.\-]+)/savegame', SaveHandler),
    webapp2.Route(r'/<token>/editing', handler=EditingHandler, name='editing')

], debug=True)