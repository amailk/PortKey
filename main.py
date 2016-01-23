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
import webapp2
from google.appengine.ext import ndb

from handler import Handler
from diary_entry import Diary

import uuid

DEFAULT_KEY = ndb.Key('KEY', "DEFAULT_KEY")

class PageHandler(Handler):
    # Status for the most recently added diary entry to be valid or invalid
    invalid = False

    def get(self):
        #Get all the diary entries, sorted by date
        diary_query = Diary.query(ancestor= DEFAULT_KEY).order(-Diary.date)
        diaries = diary_query.fetch()

        self.render("main.html", diaries=diaries, invalid=PageHandler.invalid)

class PlaceHandler(Handler):
    def post(self):
        note = self.request.get("note")
        place = self.request.get("place")
        photo = str(self.request.get("photo"))

        # Check if diary entry or place is invalid
        if len(place.strip()) == 0 or len(note.strip()) == 0:
            PageHandler.invalid = True
        else:
            PageHandler.invalid = False

            # create a new comment object
            # set a message and name to it
            new_diary = Diary(parent=DEFAULT_KEY)
            new_diary.note = note
            new_diary.place = place
            new_diary.photo = photo
            new_diary.photo_key = uuid.uuid4().hex

            # Save in the data-store
            new_diary.put()

        self.redirect("/#diaries")

    def get(self):
        diary_query = Diary.query(ancestor=DEFAULT_KEY).order(-Diary.date)
        diaries = diary_query.fetch()

        result = []
        for diary in diaries:
            result.append({"place": diary.place, "note": diary.note})

        self.response.write({"places": result})

class ImageHandler(Handler):
    def get(self):
        photo_key = self.request.get("photo_key")
        query = Diary.query(Diary.photo_key == photo_key, ancestor=DEFAULT_KEY)
        diaries = query.fetch()
        diary = diaries[0]

        if diary.photo:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(diary.photo)
        else:
            self.response.out.write('No Image')



app = webapp2.WSGIApplication([
    ('/places', PlaceHandler),
    ('/images', ImageHandler),
    ('/', PageHandler)
], debug=True)
