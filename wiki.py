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

class WikiHome(Handler):
    def get(self):
        # gmtime()
        # self.write("Show blog entries ..." + strftime("%Y-%m-%d %H:%M:%S", localtime()))
        # '2009-01-05 22:14:39'
        #blogs = self.get_blogs()
        #self.render_front()
        #self.write(blogs)
        self.get_blogs2()

    def render_front(self, subject="", content="", error=""):
        fullpagekey = 'mainpage'
        
        posts = db.GqlQuery("select * from Post "
                           " order by created desc")
        self.render("postings.html", error=error, posts=posts)


    def get_blogs2(self):
        """
            get_blogs()
            Checks the cache to see if blogs exist
            If not, call get_data_from_store and set cache

            Returns:
                A List containing blogs            
        """
        wikipages, cacheage = self.get_data_from_store()
        # cacheage = time() - lastcached
        self.render("wikis.html", error='', wikipages=wikipages, cacheage = cacheage)

    def get_data_from_store(self):
        key = "wikispage"

        cacheddata = memcache.get(key)
        if cacheddata:
            cacheage = time() - cacheddata[1]
            return cacheddata[0], cacheage
        else:
            # logging.debug("DB Query")
            wikis = db.GqlQuery("select * from Wiki "
                           " order by created desc")
            cachedTime = time()
            wikis2 = list(wikis) # force data read
            memcache.set(key, [wikis2, cachedTime])
            logging.debug("Number of wiki pages: %s", len(wikis2))
            return wikis2, 0

    def get_blogs(self):
        """
            get_blogs()
            Checks the cache to see if blogs exist
            If not, call render_front and set cache

            Returns:
                A string of HTML containing blogs            
        """

        cachedItem = memcache.get("blogs")
        if cachedItem is None or update:
            blogs = self.render_blogs()
            curtime = time()
            value = (blogs, curtime)
            if not memcache.set("blogs", value):
                logging.error("Memcache set failed")
            return blogs
        else:
            blogs, lasttime = cachedItem
            logging.debug("Returning memcached data. %s", lasttime)
            return blogs

    def render_blogs(self):
        logging.debug("DB Query")
        posts = db.GqlQuery("select * from Post "
                           " order by created desc")
        return self.render_str("postings.html", error='', posts=posts)

class WikiPage(Handler):
    def get(self):        
        self.response.write("WIKI Page")                        

    def get(self, resource):
        page = urllib.unquote(resource)
        # self.response.write("WIKI Page, resource: " + page )  
        self.render_one('data for page '+page , page, 'view', '/wiki/_edit/'+page,  'no error in ' +page )

    def render_one(self, wikidata='', page='', pageaction='', editurl='', error=''):
        #wiki = Wiki.gql("WHERE page = :1", page)
        q = db.Query(Wiki)
        q.filter('page =', page)
        wiki = q.get()
        if q.count() > 0:    
            content = wiki.content + ' row count: %s' % q.count() 
            self.render("wiki.html", content=content, pageaction=pageaction, editurl=editurl, pageid=page, error=error)
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
            # self.response.write("Welcome, %(username)s !" % {'username': username })
        else:
            self.redirect("/signup")    
            #self.response.write("Welcome, you're not autheticated")

        # self.response.write("Edit WIKI Page, resource: " + page )                        

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
        self.save(page, content, keep_history=True)
        self.redirect('/wiki/%s' % page)

    def render_one(self, content='', pageid='', pageaction='', editurl='', histurl='', error=''):        
        self.render("wiki.html", content=content, pageaction=pageaction, editurl=editurl, histurl=histurl, error=error)



    def save(self, page, content, keep_history=False):
        # wiki = Wiki.gql("WHERE page = :1", page)
        if keep_history:
            wiki = Wiki(page=page, content=content)
        else:
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


class HistoryPage(Handler):
    def get(self):        
        self.response.write("History WIKI Page")  

    def get(self, resource):
        page = urllib.unquote(resource)
        hw4_cookie = self.request.cookies.get('HW4')

        if hw4_cookie:
            username = hw4_cookie.split('|')[0]
            # self.response.write("Welcome, %(username)s !" % {'username': username })
        else:
            self.redirect("/signup")    
            #self.response.write("Welcome, you're not autheticated")

        # self.response.write("History WIKI Page, resource: " + page )                        
        self.get_pages(page)

    def get_pages(self, page):
        """
            get_blogs()
            Checks the cache to see if blogs exist
            If not, call get_data_from_store and set cache

            Returns:
                A List containing blogs            
        """
        pages = self.get_data_from_store(page)
        # cacheage = time() - lastcached
        self.render("wikihistory.html", error='', pages=pages, cacheage = 0)


    def get_data_from_store(self, page):
        # pages = Wiki.gql("WHERE page = :1", page)

        pages = db.GqlQuery("select * from Wiki where page = :1 "
                       " order by created desc", page)
        pages2 = list(pages) # force data read
        for p in pages2:
            logging.debug("db key: %s , id: %s ", p.key(), p.key().id())

        return pages2


    

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
                               ('/wiki', WikiHome),                              
                               ('/wiki/abc', WikiPage),                              
                               ('/wiki/save', EditPage),                              
                               ('/wiki/_edit/([^/]+[a-zA-Z0-9_-]+)?', EditPage),
                               ('/wiki/_history/([^/]+[a-zA-Z0-9_-]+)?', HistoryPage),
                               ('/wiki/([^/]+[a-zA-Z0-9_-]+)?', WikiPage),
                               ('/wiki(/(?:[a-zA-Z0-9_-]+/?)*)', WikiPageStar),
                               ('/wiki/.*', WekePage)
                              ],
                                 debug=True)

