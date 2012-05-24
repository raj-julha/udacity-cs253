import os
import cgi
import webapp2
import jinja2
import logging
import urllib
import json # check if webapp2 exposes any json functionality
from time import gmtime, strftime, localtime


from google.appengine.ext import db
# The entries below must be added to the app.yaml file
#libraries:
#- name: jinja2
#  version: "2.6"



template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True) # for text longer than 500 characters
    created = db.DateTimeProperty(auto_now_add = True)
    def to_json(self):
        jsontext = 'This is json from Post object'
        return jsontext
    def to_dict(self):
        retdict = {}
        retdict['subject'] = self.subject
        retdict['content'] = self.content
        retdict['created'] = str(self.created.strftime('%a %b %d %H:%M:%S %Y'))
        return retdict

class MainPage(Handler):
    def render_front(self, subject="", content="", error=""):
         #self.render("front.html", title=title, art=art, error=error, arts=arts)
        self.render("front.html", error=error)
    def get(self):
        #self.write("my blog!")
        #self.render("front.html");
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            #self.write("thanks!")
            p = Post(subject = subject, content = content)
            p.put()
            # and redirect the user to the entry
            id = p.key().id()
            s = "new post has id: %s " % id
            newposturl = "/blog/post/%s" % id
            #self.response.write(s)
            #self.redirect("/blog")
            self.redirect(newposturl)
            

        else:
            error = "We need a subject and some comments"
            #self.render("front.html", error = error)
            self.render_front(subject, content, error)

class ShowBlog(Handler):
    def render_front(self, subject="", content="", error=""):
        posts = db.GqlQuery("select * from Post "
                           " order by created desc")
        #self.render("front.html", title=title, art=art, error=error, arts=arts)
        self.render("postings.html", error=error, posts=posts)
#        self.write("Show blog entries ..." + strftime("%Y-%m-%d %H:%M:%S", localtime()))

#        for post in posts:
#            if post.subject:
#                self.response.out.write('<b>Subject: %s</b> Posted on %s ' % (post.subject, post.created))
#            else:
#                self.response.out.write('No subject')
#            self.response.out.write('<blockquote>%s</blockquote>' %
#                                    cgi.escape(post.content))



    def get(self):
        # gmtime()
        # self.write("Show blog entries ..." + strftime("%Y-%m-%d %H:%M:%S", localtime()))
        # '2009-01-05 22:14:39'
        self.render_front()

class show_single_post(Handler):
    def get(self, resource):
        param1 = urllib.unquote(resource)
        postid = param1.upper().replace('.JSON','')
        #postid = urllib.unquote(resource)
        # page displays 123&co when using url below
        # http://localhost:8080/blog/post/123&co
        # self.response.out.write(postid)
        # Now comes your code that queries the database for 
        # the single post using the image_identifier var

        id = int(postid) if postid.isdigit() else 0

        key = db.Key.from_path('Post', id)
        post = Post.get(key)
        if param1.find('.') > -1:
            self.render_json(post)
        else:
            self.render_one(post)

    def render_debug(self, id, key, post):
        self.response.write("id: %s" % id) 
        self.response.write("<br>")
        self.response.write("key: %s " % key) 
        self.response.write("<br>")
        self.response.write("created: %s" % post.created)
        self.response.write("<br>")
        self.response.write("subject: %s" % cgi.escape(post.subject))
        self.response.write("<br>")
        self.response.write("content: %s" % cgi.escape(post.content))
        self.response.write("<br>")


    def render_one(self, post):
        self.render("oneentry.html", post=post)


    def render_json(self, post):
        self.response.headers['Content-Type'] = 'application/json'

        jsontext = json.dumps(post.to_dict(), indent=4)
        deser = json.loads(jsontext)
        logging.debug('deser: %s ', deser)
        logging.debug('content: %s ', deser['content'])
        self.response.out.write(jsontext)

class ShowJson(Handler):
    def render_front(self, subject="", content="", error=""):
        posts = db.GqlQuery("select * from Post "
                           " order by created desc")

        #self.render("postings.html", error=error, posts=posts)
        #self.write("Show blog entries ..." + strftime("%Y-%m-%d %H:%M:%S", localtime()))

        # TypeError: <google.appengine.ext.db.GqlQuery object at 0x41bbf50> is not JSON serializable
        #self.response.out.write(json.dumps(posts))

        self.response.headers['Content-Type'] = 'application/json'
        jsonlist = []
        for post in posts:
            jsonlist.append(post.to_dict())

        jsontext = json.dumps(jsonlist)
        deser = json.loads(jsontext)
        logging.debug('deser: %s ', deser)
        self.response.out.write(json.dumps(jsonlist, indent=4))


    def get(self):
        # gmtime()
        # self.write("Show blog entries ..." + strftime("%Y-%m-%d %H:%M:%S", localtime()))
        # '2009-01-05 22:14:39'
        self.render_front()

class ShowOneJson(Handler):
    def get(self, resource):
        param1 = urllib.unquote(resource)
        postid = param1.upper().replace('.JSON','')
        # page displays 123&co when using url below
        # http://localhost:8080/blog/post/123&co
        # self.response.out.write(postid)
        # Now comes your code that queries the database for 
        # the single post using the image_identifier var

        logging.debug('postid: %s', postid)
        id = int(postid) if postid.isdigit() else 0

        key = db.Key.from_path('Post', id)
        post = Post.get(key)
        self.render_one(post)

    def render_debug(self, id, key, post):
        self.response.write("id: %s" % id) 
        self.response.write("<br>")
        self.response.write("key: %s " % key) 
        self.response.write("<br>")
        self.response.write("created: %s" % post.created)
        self.response.write("<br>")
        self.response.write("subject: %s" % cgi.escape(post.subject))
        self.response.write("<br>")
        self.response.write("content: %s" % cgi.escape(post.content))
        self.response.write("<br>")


    def render_one(self, post):
        self.response.headers['Content-Type'] = 'application/json'

        jsonlist.append(post.to_dict())

        jsontext = json.dumps(post.to_dict(), indent=4)
        deser = json.loads(jsontext)
        logging.debug('deser: %s ', deser)
        self.response.out.write(jsontext)

# tegexp below states any characters other than /
# ('/blog/post/([^/]+)?', show_single_post)
#           ('/blog/post(/?[0-9]+)', show_single_post)

# working 05-May 12:32
# - url: /blog/post(/?[0-9]+)
# ('/blog/post(/?[0-9]+)', show_single_post)
# http://localhost:8080/blog/post/123 shows /123

app = webapp2.WSGIApplication([
                               ('/blog', ShowBlog),
                               ('/blog/newpost', MainPage),
                               ('/blog/post/([^/]+)?', show_single_post),
                               ('/blog/showpost/([^/]+)?', show_single_post),
                               ('/blog/\.json', ShowJson),
                               ('/blog/post/([^/]+)?\.json', ShowOneJson)
                              ],
                                 debug=True)