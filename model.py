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
    email = db.StringProperty(required = False)
    salt = db.StringProperty(required = False)
    passwordhash = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Wiki(db.Model):
    page = db.StringProperty(required = True)    
    content = db.TextProperty(required = False) # for text longer than 500 characters
    createdby = db.StringProperty(required = False)
    updatedby = db.StringProperty(required = False)
    created = db.DateTimeProperty(auto_now_add = True)
    updated = db.DateTimeProperty(required = False, auto_now=False)


