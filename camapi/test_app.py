# test_app.py
 
 
import os
import unittest
 
from app import app
import random, string  

# 6 char random string
def get_random_id():
    return ''.join(random.SystemRandom(). \
    choice(string.ascii_uppercase + string.digits) for _ in range(6))

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
 
    def test_index(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
 
    def test_logs(self):
        response = self.app.get('/logs', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

 
if __name__ == "__main__":
    unittest.main()