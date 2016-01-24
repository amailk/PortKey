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
import datetime
from google.appengine.ext import ndb

from handler import Handler
from diary_entry import Diary

import uuid
import json

from google.appengine.api import images
from google.appengine.api import users

DEFAULT_KEY = ndb.Key('KEY', "DEFAULT_KEY")

class PageHandler(Handler):
    # Status for the most recently added diary entry to be valid or invalid
    invalidPlace = False
    invalidNote = False
    invalidPhoto = False

    def get(self):
        user = users.get_current_user()

        if user:
            #Get all the diary entries, sorted by date
            diary_query = Diary.query(Diary.user_id == user.user_id(), ancestor=DEFAULT_KEY).order(-Diary.date)
            diaries = diary_query.fetch()
            for diary in diaries:
                diary.date_text = diary.date.strftime('%Y, %b %d')
            self.render("main.html", diaries=diaries, invalidPlace=PageHandler.invalidPlace, invalidNote=PageHandler.invalidNote, invalidPhoto=PageHandler.invalidPhoto, logout_url=users.create_logout_url('/login'))
        else:
            self.redirect("/login")



class PlaceHandler(Handler):
    def post(self):
        note = self.request.get("note")
        place = self.request.get("place")
        photo = str(self.request.get("photo"))

        user = users.get_current_user()
        
        if user:
            invalidFieldFlag = False
            # Check if diary entry or place is invalid
            if len(place.strip()) == 0:
                PageHandler.invalidPlace = True
                invalidFieldFlag = True
            if len(note.strip()) == 0:
                PageHandler.invalidNote = True
                invalidFieldFlag = True
            if len(photo.strip()) < 100:
                PageHandler.invalidPhoto = True
                invalidFieldFlag = True

            if not invalidFieldFlag:
                PageHandler.invalidPlace = PageHandler.invalidNote = PageHandler.invalidPhoto = False

                new_diary = Diary(parent=DEFAULT_KEY)
                new_diary.note = note
                new_diary.place = place
                new_diary.photo = photo
                new_diary.photo_key = uuid.uuid4().hex
                new_diary.user_id = user.user_id()


                # Save in the data-store
                new_diary.put()

            self.redirect("/#diaries")
        else:
            self.redirect("/login")


    def get(self):
        diary_query = Diary.query(ancestor=DEFAULT_KEY).order(-Diary.date)
        diaries = diary_query.fetch()

        result = []
        for diary in diaries:
            result.append({"place": diary.place, "note": diary.note, "photoKey": diary.photo_key})

        self.response.write(json.dumps({"places": result}))

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

class LoginHandler(Handler):
    def get(self):
        self.render("login.html", url=users.create_login_url('/'))

app = webapp2.WSGIApplication([
    ('/login', LoginHandler),
    ('/places', PlaceHandler),
    ('/images', ImageHandler),
    ('/', PageHandler)
], debug=True)
