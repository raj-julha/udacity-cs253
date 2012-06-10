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

from basehandler import *

# The entries below must be added to the app.yaml file
#libraries:
#- name: jinja2
#  version: "2.6"



template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class HomePage(Handler):
    def get(self):        
        # self.response.write("Raj Julha Udacity CS253 Home Page")                        
        self.render_front()

    def render_front(self, error=""):
         #self.render("front.html", title=title, art=art, error=error, arts=arts)
        self.render("home.html", error=error)
                        

# class HomePage(webapp2.RequestHandler):
app = webapp2.WSGIApplication([
                               ('/', HomePage)                            
                              ],
                                 debug=True)

