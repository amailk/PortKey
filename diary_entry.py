from google.appengine.ext import ndb

# Object represents a diary entry
class Diary(ndb.Model):
    place = ndb.StringProperty(indexed=False)
    note = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)