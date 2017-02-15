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
import jinja2
import os
import cgi
from google.appengine.ext import db


# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


class Post(db.Model):
    title = db.StringProperty(required = True)
    postContent = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)



class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template_file, **params):
        template = jinja_env.get_template(template_file)
        return template.render(params)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))


class MainHandler(Handler):
    def get(self):
        self.response.write('Hello world!')


class BlogDisplay(Handler):
    def get(self):
        post_list = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")

        self.render("blogdisplay.html", error="", post_list=post_list)


class NewPost(Handler):
    def get(self):
        self.render("newpost.html", title="", postContent="", error="")

    def post(self):
        title = self.request.get('title')
        postContent = self.request.get('postContent')
        escaped_title = cgi.escape(title, quote=True)
        escaped_postContent = cgi.escape(postContent, quote=True)

        if title == "" or postContent == "":
            error = "You need both a Title and Content."
            self.render("newpost.html", error=error, title=escaped_title, postContent=postContent)
        else:
            post = Post(title=escaped_title, postContent=escaped_postContent)
            post.put()
            self.redirect("/blog")




app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogDisplay),
    ('/newpost', NewPost)
], debug=True)
