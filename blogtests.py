import unittest
from google.appengine.api import memcache
from google.appengine.ext import testbed


class DemoTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_memcache_stup()

    def tearDown(self):
        self.testbed.deactivate()

if __name__ == '__main__':
    unittest.main()

