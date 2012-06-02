import os
import cgi
import webapp2
import jinja2
import logging
import urllib
import json # check if webapp2 exposes any json functionality
from time import gmtime, strftime, localtime, time


from google.appengine.ext import db
from google.appengine.api import memcache

from model import *

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


class WekePage(Handler):
    def get(self):        
        self.response.write("WeKe Page")                        

    def get(self, resource):
        param1 = urllib.unquote(resource)
        self.response.write("WEKE Page, resource: " + param1 )                        


class WikiPage(Handler):
    def get(self):        
        self.response.write("WIKI Page")                        

    def get(self, resource):
        page = urllib.unquote(resource)
        self.response.write("WIKI Page, resource: " + page )  
        #self.render_one(param1, param1, '/wiki/_edit/'+page,  'no error')
        self.render_one('data for page '+page , page, 'view', '/wiki/_edit/'+page,  'no error')

    def render_one(self, wikidata='', page='', pageaction='', editurl='', error=''):
        #wiki = Wiki.gql("WHERE page = :1", page)
        q = db.Query(Wiki)
        q.filter('page =', page)
        wiki = q.get()
        if q.count() > 0:    
            content = wiki.content + ' row count: %s' % q.count() 
            self.render("wiki.html", content=content, pageaction=pageaction, editurl=editurl, error=error)
        else:
            #content = 'No data' 
            self.redirect('/wiki/_edit/%s' % page )




class WikiPageStar(Handler):
    def get(self):        
        self.response.write("WikiPageStar WIKI Page")                        

    def get(self, resource):
        param1 = urllib.unquote(resource)
        self.response.write("WikiPageStar WIKI Page, resource: " + param1 )                        


class EditPage(Handler):
    def get(self):        
        self.response.write("Edit WIKI Page")  

    def get(self, resource):
        page = urllib.unquote(resource)
        hw4_cookie = self.request.cookies.get('HW4')

        if hw4_cookie:
            username = hw4_cookie.split('|')[0]
            self.response.write("Welcome, %(username)s !" % {'username': username })
        else:
            #self.redirect("/wiki/signup")    
            self.response.write("Welcome, you're not autheticated")

        self.response.write("Edit WIKI Page, resource: " + page )                        
        #self.render_one(param1, param1, '/wiki/_edit/'+page,  'no error')
        wiki = self.get_wiki(page=page)
        if wiki:
            self.render_one(wiki.content, page, 'edit', '/wiki/'+page,  'no error')
        else:            
            self.render_one('empty page', page, 'edit', '/wiki/_edit/'+page,  'no error')
            #self.redirect('/wiki/_edit/%s' % page)

    def post(self, resource):
        page = urllib.unquote(resource)
        self.response.write("resource: " + page)
        content = cgi.escape(self.request.get('content'), quote = True)
        # content = self.request.get('content')
        self.response.write("WIKI Saved: " + content )
        self.response.write("<br>WIKI escaped: " + cgi.escape(self.request.get('content'), quote = True))
        self.save(page, content)
        self.redirect('/wiki/%s' % page)

    def render_one(self, content='', pageid='', pageaction='', editurl='', error=''):        
        self.render("wiki.html", content=content, pageaction=pageaction, editurl=editurl, error=error)



    def save(self, page, content):
        # wiki = Wiki.gql("WHERE page = :1", page)
        q = db.Query(Wiki)
        q.filter('page =', page)
        wiki = q.get()

        if q.count() > 0:    
            wiki.content = content
        else:
            wiki = Wiki(page=page, content=content)

        wiki.put()

    def get_wiki(self, page):
        # wiki = Wiki.gql("WHERE page = :1", page)
        q = db.Query(Wiki)
        q.filter('page =', page)
        wiki = q.get()

        if q.count() > 0:    
            return wiki
        else:
            return None

    

# tegexp below states any characters other than /
# ('/blog/post/([^/]+)?', show_single_post)
#           ('/blog/post(/?[0-9]+)', show_single_post)

# working 05-May 12:32
# - url: /blog/post(/?[0-9]+)
# ('/blog/post(/?[0-9]+)', show_single_post)
# http://localhost:8080/blog/post/123 shows /123

# ('/blog/post/([^/]+)?', show_single_post),
# /wiki(/(?:[a-zA-Z0-9_-]+/?)*)
#                                ('/wiki'+ PAGE_RE, WikiPage),
PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([
                               ('/wiki/abc', WikiPage),                              
                               ('/wiki/save', EditPage),                              
                               ('/wiki/_edit/([^/]+[a-zA-Z0-9_-]+)?', EditPage),
                               ('/wiki/([^/]+[a-zA-Z0-9_-]+)?', WikiPage),
                               ('/wiki(/(?:[a-zA-Z0-9_-]+/?)*)', WikiPageStar),
                               ('/wiki/.*', WekePage)
                              ],
                                 debug=True)

