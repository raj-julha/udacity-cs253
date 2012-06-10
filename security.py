import uuid
import hmac
import logging
# Implement the hash_str function to use HMAC and our SECRET instead of md5
SECRET = 'inspiron'

def hash_str(s, salt=None):
    # return hmac.new(SECRET, s).hexdigest()

    if salt == None:
        newsalt = str(uuid.uuid4())
    else:
        # Exception TypeError: character mapping must return integer, None or unicode
        # is raised if we don't explicitly convert salt using str
        newsalt = str(salt) 

    return newsalt, hmac.new(newsalt, s).hexdigest()

def make_secure_val(s, salt=None):
    newsalt, hashstr = hash_str(s, salt)
    return "%s|%s" % (s, hashstr)

def check_secure_val(h, salt=None):
    val = h.split('|')[0]
    if h == make_secure_val(val, salt):
        return val

def write_authentication_cookie(resp, username, pwdhash):
    hw4 = str('HW4=%s|%s; Path=/' % (username, pwdhash))
    logging.debug(hw4)
    resp.headers.add_header('Set-Cookie', hw4)

def delete_authentication_cookie(resp):
    #resp.delete_cookie('HW4')
    hw4 = str('HW4=; Path=/')
    resp.headers.add_header('Set-Cookie', hw4)
