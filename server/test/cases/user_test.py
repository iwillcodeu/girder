import cherrypy
import json

from .. import base

def setUpModule():
    base.startServer()

def tearDownModule():
    base.stopServer()

class UserTestCase(base.TestCase):
    def _verifyAuthCookie(self, resp):
        self.assertTrue(resp.cookie.has_key('authToken'))
        cookieVal = json.loads(resp.cookie['authToken'].value)
        self.assertHasKeys(cookieVal, ['token', 'userId'])
        self.assertEqual(resp.cookie['authToken']['expires'],
                         cherrypy.config['sessions']['cookie_lifetime'] * 3600 * 24)

    def testRegisterAndLoginBcrypt(self):
        """
        Test user registration and logging in.
        """
        cherrypy.config['auth']['hash_alg'] = 'bcrypt'
        cherrypy.config['auth']['bcrypt_rounds'] = 4 # Set this to minimum so test runs faster.

        params = {
            'email' : 'bad_email',
            'login' : 'illegal@login',
            'firstName' : 'First',
            'lastName' : 'Last',
            'password' : 'bad'
        }
        # First test all of the required parameters.
        self.ensureRequiredParams(path='/user', method='POST', required=params.keys())

        # Now test parameter validation
        resp = self.request(path='/user', method='POST', params=params)
        self.assertStatus(resp, 400)
        self.assertEqual('Login may not have an "@" character.', resp.json['message'])

        params['login'] = 'goodlogin'
        resp = self.request(path='/user', method='POST', params=params)
        self.assertStatus(resp, 400)
        self.assertEqual(cherrypy.config['users']['password_description'], resp.json['message'])

        params['password'] = 'goodpassword'
        resp = self.request(path='/user', method='POST', params=params)
        self.assertStatus(resp, 400)
        self.assertEqual('Invalid email address.', resp.json['message'])

        # Now successfully create the user
        params['email'] = 'good@email.com'
        resp = self.request(path='/user', method='POST', params=params)
        self.assertStatusOk(resp)
        self.assertHasKeys(resp.json, ['_id', 'firstName', 'lastName', 'email', 'login',
                                       'admin', 'size', 'hashAlg'])
        self.assertNotHasKeys(resp.json, ['salt'])
        self.assertEqual(resp.json['hashAlg'], 'bcrypt')

        # Now that our user is created, try to login
        params = {
            'login' : 'incorrect@email.com',
            'password' : 'badpassword'
        }
        self.ensureRequiredParams(path='/user/login', method='POST', required=params.keys())

        # Login with unregistered email
        resp = self.request(path='/user/login', method='POST', params=params)
        self.assertStatus(resp, 403)
        self.assertEqual('Login failed.', resp.json['message'])

        # Correct email, but wrong password
        params['login'] = 'good@email.com'
        resp = self.request(path='/user/login', method='POST', params=params)
        self.assertStatus(resp, 403)
        self.assertEqual('Login failed.', resp.json['message'])

        # Login successfully with email
        params['password'] = 'goodpassword'
        resp = self.request(path='/user/login', method='POST', params=params)
        self.assertStatusOk(resp)

        # Invalid login
        params['login'] = 'badlogin'
        resp = self.request(path='/user/login', method='POST', params=params)
        self.assertStatus(resp, 403)
        self.assertEqual('Login failed.', resp.json['message'])

        # Login successfully with login
        params['login'] = 'goodlogin'
        resp = self.request(path='/user/login', method='POST', params=params)
        self.assertStatusOk(resp)

        # Make sure we got a nice cookie
        self._verifyAuthCookie(resp)

    def testRegisterAndLoginSha512(self):
        cherrypy.config['auth']['hash_alg'] = 'sha512'

        params = {
            'email' : 'good@email.com',
            'login' : 'goodlogin',
            'firstName' : 'First',
            'lastName' : 'Last',
            'password' : 'goodpassword'
        }

        # Register a user with sha512 storage backend
        resp = self.request(path='/user', method='POST', params=params)
        self.assertStatusOk(resp)
        self.assertHasKeys(resp.json, ['_id', 'firstName', 'lastName', 'email', 'login',
                                       'admin', 'size', 'hashAlg'])
        self.assertNotHasKeys(resp.json, ['salt'])
        self.assertEqual(resp.json['hashAlg'], 'sha512')

        # Login unsuccessfully
        resp = self.request(path='/user/login', method='POST', params={
          'login' : params['login'],
          'password' : params['password'] + '.'
          })
        self.assertStatus(resp, 403)
        self.assertEqual('Login failed.', resp.json['message'])

        # Login successfully
        resp = self.request(path='/user/login', method='POST', params={
          'login' : params['login'],
          'password' : params['password']
          })
        self.assertStatusOk(resp)
        self.assertEqual('Login succeeded.', resp.json['message'])

        # Make sure we got a nice cookie
        self._verifyAuthCookie(resp)




