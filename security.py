import hmac
import logging
# Implement the hash_str function to use HMAC and our SECRET instead of md5
SECRET = 'inspiron'
def hash_str(s):
    ###Your code here
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val

def write_authentication_cookie(resp, username, pwdhash):
    hw4 = str('HW4=%s|%s; Path=/' % (username, pwdhash))
    logging.debug(hw4)
    resp.headers.add_header('Set-Cookie', hw4)

def delete_authentication_cookie(resp):
    #resp.delete_cookie('HW4')
    hw4 = str('HW4=; Path=/')
    resp.headers.add_header('Set-Cookie', hw4)
