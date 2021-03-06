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

def get_posts(limit, offset):
    post_list = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT  %s OFFSET %s" % (limit,offset))
    return post_list

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
        pageNum = self.request.get('page')
        page_limit = 5
        if not pageNum or pageNum[0]=='-':
            pageNum = 0
        offset = int(pageNum) * page_limit - page_limit
        if offset < 0:
            offset = 0

        post_list = get_posts(page_limit, offset)

        next_link = ['','']
        prev_link = ['','']
        if post_list.count(offset=offset+page_limit, limit=page_limit) > 0:
            next_link[0] = "\\blog?page=%s" % (str(int(pageNum)+1),)
            next_link[1] = "Next Page"
        if post_list.count(offset=offset-page_limit, limit=page_limit) > 0 and pageNum > 0:
            prev_link[0] = "\\blog?page=%s" % (str(int(pageNum)-1),)
            prev_link[1] = "Previous Page"

        self.render("blogdisplay.html", error="", post_list=post_list, next_link=next_link, prev_link=prev_link)


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
            self.redirect("/blog/"+str(post.key().id()))


class ViewPostHandler(Handler):
    def get(self, id):
        post = []
        post.append(Post.get_by_id(int(id)))
        if post[0] == None:
            error = "There is no post with that ID"
        else:
            error = ""
        self.render("singlepost.html", error=error, post_list=post)



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogDisplay),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
