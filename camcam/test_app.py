# test_app.py
 
 
import os
import unittest
 
from app import app
  
 
class BasicTests(unittest.TestCase):
 
    #
    # setup and teardown 
    #
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()


 
    # executed after each test
    def tearDown(self):
        pass
 
 
#
# tests 
#
 
    def test_random_event(self):
        result = app.log_random_event()
        self.assertNotEqual(result, "")
 
 
if __name__ == "__main__":
    unittest.main()