from google.appengine.ext import ndb
class User(ndb.Model):
    token = ndb.StringProperty()
    game = ndb.TextProperty()

