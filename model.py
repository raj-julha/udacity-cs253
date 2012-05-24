import os
import cgi
import webapp2
import jinja2
import logging
import urllib
from time import gmtime, strftime, localtime
from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty(required = True)
    #password = db.StringProperty(required = True) 
    email = db.StringProperty(required = False)
    passwordhash = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

