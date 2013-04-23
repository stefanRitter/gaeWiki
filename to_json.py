
import webapp2
import json
import time

from data import *


def convert_post_to_obj(post):
    p = {}
    p['subject'] = post.subject
    p['content'] = post.content
    p['created'] = post.created.strftime("%a %b %d %H:%M:%S %Y")
    return p


class JsonBlogHandler(webapp2.RequestHandler):
    def get(self):
        json_blog = []
        posts = db.GqlQuery('select * from Post order by created DESC')
        for post in posts:
            jp = convert_post_to_obj(post)
            json_blog.append(jp)

        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.out.write(json.dumps(json_blog))


class JsonPostHandler(webapp2.RequestHandler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        if post:
            p = convert_post_to_obj(post)
            self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
            self.response.out.write(json.dumps(p))

        else:
            self.redirect('/blog')
