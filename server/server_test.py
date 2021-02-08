import unittest
import requests

import database_helper as db

# API endpoint
URL = 'http://127.0.0.1:5000/'
SAMPLE_USER = {
    'email': 'peter@pan.com',
    'password': '123456',
    'firstname': 'Peter',
    'familyname': 'Pan',
    'gender': 'Male',
    'city': 'London',
    'country': 'Neverland',
}
SAMPLE_USER2 = {
    'email': 'tinge@ling.com',
    'password': 'qwerty123',
    'firstname': 'Tinker',
    'familyname': 'Bell',
    'gender': 'Female',
    'city': 'Manchester',
    'country': 'Neverland',
}
SAMPLE_MSG = 'The moment you doubt whether you can fly, you cease for ever to be able to do it.'
SAMPLE_MSG2 = 'Never say goodbye because goodbye means going away and going away means forgetting.'


class TestServer(unittest.TestCase):
    def testWelcome(self):
        r = requests.get(URL)
        data, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(data['response'], 'Welcome to Twidder')


class TestSignUp(unittest.TestCase):
    def setUp(self):
        """ Restore database before each test. """
        db.create_db()

    def testSignUpUser(self):
        data = SAMPLE_USER.copy()
        r = requests.post(URL + 'sign_up', json=data)
        data, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(data['message'], 'Successfully created a new user.')

    def testSignUpUserAlreadyExists(self):
        data = SAMPLE_USER.copy()
        requests.post(URL + 'sign_up', json=data)  # Sign up once.
        r = requests.post(URL + 'sign_up', json=data)  # Sign up again.
        data, code = r.json()
        self.assertEqual(code, 204)
        self.assertEqual(data['message'], 'User already exists.')

    def testSignUpUserWithBadData(self):
        data = SAMPLE_USER.copy()
        data.pop('email')  # Remove email field.
        r = requests.post(URL + 'sign_up', json=data)
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data missing.')

    def testSignUpUserWithTooShortPassword(self):
        data = SAMPLE_USER.copy()
        data['password'] = '12345'  # Make password too short.
        r = requests.post(URL + 'sign_up', json=data)
        data, code = r.json()
        self.assertEqual(code, 204)
        self.assertEqual(data['message'], 'Password is not long enough.')

    def testSignUpUserWithTooLongPassword(self):
        data = SAMPLE_USER.copy()
        data['password'] = '1'*51  # Make password too long.
        r = requests.post(URL + 'sign_up', json=data)
        data, code = r.json()
        self.assertEqual(code, 204)
        self.assertEqual(data['message'], 'Password is too long.')

    def testSignUpUserWithBadType(self):
        data = SAMPLE_USER.copy()
        data['password'] = 123456  # Make password wrong type.
        r = requests.post(URL + 'sign_up', json=data)
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data has incorrect type.')


class TestSignIn(unittest.TestCase):
    def setUp(self):
        """ Create a user for each test. """
        db.create_db()
        data = SAMPLE_USER.copy()
        db.create_user(**data)

    def testSignInUser(self):
        data = SAMPLE_USER.copy()
        r = requests.post(URL + 'sign_in', json=data)
        data, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(data['message'], 'Successfully signed in.')
        self.assertEqual(len(data['data']), 36)  # token

    def testSignInUserWrongPassword(self):
        data = SAMPLE_USER.copy()
        data['password'] = '654321'  # Supply wrong password.
        r = requests.post(URL + 'sign_in', json=data)
        data, code = r.json()
        self.assertEqual(code, 401)
        self.assertEqual(data['message'], 'Wrong username or password.')

    def testSignInUserWrongEmail(self):
        data = SAMPLE_USER.copy()
        data['email'] = SAMPLE_USER2['email']  # Supply wrong email.
        r = requests.post(URL + 'sign_in', json=data)
        data, code = r.json()
        self.assertEqual(code, 401)
        self.assertEqual(data['message'], 'Wrong username or password.')

    def testSignInUserWithBadType(self):
        data = SAMPLE_USER.copy()
        data['password'] = 123456  # Make password wrong type.
        r = requests.post(URL + 'sign_in', json=data)
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data has incorrect type.')

    def testSignInUserWithBadData(self):
        data = SAMPLE_USER.copy()
        data.pop('email')  # Remove email field.
        r = requests.post(URL + 'sign_in', json=data)
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data missing.')


class TestSignOut(unittest.TestCase):
    def setUp(self):
        """ Create a user for each test. """
        db.create_db()
        data = SAMPLE_USER.copy()
        db.create_user(**data)

    def test_sign_out_user(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'sign_out',
                          headers={'authorization': token}, json={})
        data, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(data['message'], 'Successfully signed out.')

    def test_sign_out_user_with_bad_token(self):
        r = requests.post(
            URL + 'sign_out', headers={'authorization': '1'*36}, json={})
        data, code = r.json()
        self.assertEqual(code, 401)
        self.assertEqual(data['message'], 'You are not signed in.')

    def testSignOutUserWithBadData(self):
        r = requests.post(URL + 'sign_out', json={})  # Don't supply token.
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data missing.')


class TestChangePassword(unittest.TestCase):
    def setUp(self):
        """ Create a user for each test. """
        db.create_db()
        data = SAMPLE_USER.copy()
        db.create_user(**data)

    def testChangePassword(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'change_password', headers={
                          'authorization': token}, json={'oldPassword': data['password'], 'newPassword': 'newPassword'})
        rdata, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(rdata['message'], 'Password changed.')
        self.assertTrue(db.has_password(data['email'], 'newPassword'))
        self.assertFalse(db.has_password(data['email'], data['password']))

    def testNewPasswordTooShort(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'change_password', headers={
                          'authorization': token}, json={'oldPassword': data['password'], 'newPassword': '12345'})
        data, code = r.json()
        self.assertEqual(code, 204)
        self.assertEqual(data['message'], 'Password is not long enough.')

    def testNewPasswordTooLong(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'change_password', headers={
                          'authorization': token}, json={'oldPassword': data['password'], 'newPassword': '1'*51})
        data, code = r.json()
        self.assertEqual(code, 204)
        self.assertEqual(data['message'], 'Password is too long.')

    def testWrongOldPassword(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'change_password', headers={
                          'authorization': token}, json={'oldPassword': 'wrongPassword', 'newPassword': 'newPassword'})
        rdata, code = r.json()
        self.assertEqual(code, 401)
        self.assertEqual(rdata['message'], 'Wrong password.')
        self.assertFalse(db.has_password(data['email'], 'newPassword'))
        self.assertTrue(db.has_password(data['email'], data['password']))

    def testChangePasswordWithBadToken(self):
        data = SAMPLE_USER.copy()
        r = requests.post(URL + 'change_password', headers={
                          'authorization': '1'*36}, json={'oldPassword': 'wrongPassword', 'newPassword': 'newPassword'})
        rdata, code = r.json()
        self.assertEqual(code, 401)
        self.assertEqual(rdata['message'], 'You are not logged in.')
        self.assertFalse(db.has_password(data['email'], 'newPassword'))
        self.assertTrue(db.has_password(data['email'], data['password']))

    def testChangePasswordWithBadType(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'change_password', headers={
                          'authorization': token}, json={'oldPassword': data['password'], 'newPassword': 123456})
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data has incorrect type.')

    def testChangePasswordWithBadData(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'change_password', headers={
                          'authorization': token}, json={'oldPassword': data['password']})
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data missing.')


class TestGetUserDataByToken(unittest.TestCase):
    def setUp(self):
        """ Create a user for each test. """
        db.create_db()
        data = SAMPLE_USER.copy()
        db.create_user(**data)

    def test_get_user_data_by_token(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.get(URL + 'get_user_data_by_token',
                         headers={'authorization': token}, json={})
        data, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(data['message'], 'User data retrieved.')
        expected_data = SAMPLE_USER.copy()
        expected_data.pop('password')
        self.assertEqual(data['data'], expected_data)

    def test_get_user_data_with_no_token(self):
        # Don't supply token.
        r = requests.get(URL + 'get_user_data_by_token', headers={}, json={})
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data missing.')


class TestGetUserDataByEmail(unittest.TestCase):
    def setUp(self):
        """ Create a user for each test. """
        db.create_db()
        data = SAMPLE_USER.copy()
        db.create_user(**data)
        data = SAMPLE_USER2.copy()
        db.create_user(**data)

    def test_get_user_data_by_email(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.get(URL + 'get_user_data_by_email/' + SAMPLE_USER2['email'],
                         headers={'authorization': token}, json={})
        data, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(data['message'], 'User data retrieved.')
        expected_data = SAMPLE_USER2.copy()
        expected_data.pop('password')
        self.assertEqual(data['data'], expected_data)

    def test_get_user_data_with_bad_email(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.get(URL + 'get_user_data_by_email/' + 'not_a@user.com',
                         headers={'authorization': token}, json={})  # Give bad email.
        data, code = r.json()
        self.assertEqual(code, 204)
        self.assertEqual(data['message'], 'No such user.')

    def test_get_user_data_with_bad_token(self):
        r = requests.get(URL + 'get_user_data_by_email/' + SAMPLE_USER2['email'],
                         headers={'authorization': '1'*36}, json={})  # Give bad token.
        data, code = r.json()
        self.assertEqual(code, 401)
        self.assertEqual(data['message'], 'You are not logged in.')

    def test_get_user_data_with_no_token(self):
        r = requests.get(URL + 'get_user_data_by_email/' +
                         SAMPLE_USER2['email'], json={})  # Don't supply token.
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data missing.')


class TestGetUserMessagesByToken(unittest.TestCase):
    def setUp(self):
        """ Create a user for each test. """
        db.create_db()
        data = SAMPLE_USER.copy()
        db.create_user(**data)

    def testGetNoMessages(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.get(URL + 'get_user_messages_by_token',
                         headers={'authorization': token}, json={})
        rdata, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(rdata['message'], 'User messages retrieved.')
        self.assertEqual(rdata['data'], [])

    def testGetOneMessage(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        requests.post(URL + 'post_message', headers={'authorization': token}, json={
                      'email': data['email'], 'message': SAMPLE_MSG})
        r = requests.get(URL + 'get_user_messages_by_token',
                         headers={'authorization': token})
        rdata, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(rdata['message'], 'User messages retrieved.')
        self.assertEqual(rdata['data'], [
                         {'id': 1, 'writer': data['email'], 'recipient': data['email'], 'content': SAMPLE_MSG}])

    def testGetMultipleMessages(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        requests.post(URL + 'post_message', headers={'authorization': token}, json={
                      'email': data['email'], 'message': SAMPLE_MSG})
        requests.post(URL + 'post_message', headers={'authorization': token}, json={
                      'email': data['email'], 'message': SAMPLE_MSG2})
        r = requests.get(URL + 'get_user_messages_by_token',
                         headers={'authorization': token}, json={})
        rdata, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(rdata['message'], 'User messages retrieved.')
        self.assertEqual(rdata['data'], [
                         {'id': 1, 'writer': data['email'],
                             'recipient': data['email'], 'content': SAMPLE_MSG},
                         {'id': 2, 'writer': data['email'],
                             'recipient': data['email'], 'content': SAMPLE_MSG2},
                         ])

    def testGetMessagesWithBadData(self):
        # Don't supply token.
        r = requests.get(URL + 'get_user_messages_by_token',
                         headers={}, json={})
        rdata, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(rdata['message'], 'Form data missing.')

    def testGetMessagesWithBadToken(self):
        r = requests.get(URL + 'get_user_messages_by_token',
                         headers={'authorization': '1'*36}, json={})  # Supply bad token.
        rdata, code = r.json()
        self.assertEqual(code, 401)
        self.assertEqual(rdata['message'], 'You are not logged in.')


class TestGetUserMessagesByEmail(unittest.TestCase):
    def setUp(self):
        """ Create a user for each test. """
        db.create_db()
        data = SAMPLE_USER.copy()
        db.create_user(**data)
        data = SAMPLE_USER2.copy()
        db.create_user(**data)
        data = SAMPLE_USER.copy()
        db.post_message(SAMPLE_USER['email'],
                        SAMPLE_USER2['email'], SAMPLE_MSG)

    def testGetOneMessage(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        requests.post(URL + 'post_message', headers={'authorization': token}, json={
                      'email': data['email'], 'message': SAMPLE_MSG})
        r = requests.get(URL + 'get_user_messages_by_email/' + SAMPLE_USER2['email'],
                         headers={'authorization': token}, json={})
        rdata, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(rdata['message'], 'User messages retrieved.')
        self.assertEqual(rdata['data'], [
                         {'id': 1, 'writer': data['email'], 'recipient': SAMPLE_USER2['email'], 'content': SAMPLE_MSG}])

    def testGetMessagesWithBadToken(self):
        r = requests.get(URL + 'get_user_messages_by_email/' + SAMPLE_USER2['email'],
                         headers={'authorization': '1'*36}, json={})  # Supply bad token.
        rdata, code = r.json()
        self.assertEqual(code, 401)
        self.assertEqual(rdata['message'], 'You are not logged in.')


class TestPostMessage(unittest.TestCase):
    def setUp(self):
        """ Create a user for each test. """
        db.create_db()
        data = SAMPLE_USER.copy()
        db.create_user(**data)
        data = SAMPLE_USER2.copy()
        db.create_user(**data)

    def testSendMessageToSelf(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'post_message', headers={'authorization': token}, json={
                          'email': data['email'], 'message': SAMPLE_MSG})
        rdata, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(rdata['message'], 'Message posted.')

    def testSendMessageToOtherUser(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'post_message', headers={'authorization': token}, json={
                          'email': SAMPLE_USER2['email'], 'message': SAMPLE_MSG})
        rdata, code = r.json()
        self.assertEqual(code, 200)
        self.assertEqual(rdata['message'], 'Message posted.')

    def testSendTooLongMessage(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        r = requests.post(URL + 'post_message', headers={'authorization': token}, json={
                          'email': SAMPLE_USER2['email'], 'message': '1'*501})
        rdata, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(rdata['message'], 'Message was too long.')

    def testPostMessageWithBadToken(self):
        data = SAMPLE_USER.copy()
        r = requests.post(URL + 'post_message', headers={'authorization': '1'*36}, json={
                          'email': SAMPLE_USER2['email'], 'message': SAMPLE_MSG})
        rdata, code = r.json()
        self.assertEqual(code, 401)
        self.assertEqual(rdata['message'], 'You are not logged in.')
        self.assertFalse(db.has_password(data['email'], 'newPassword'))
        self.assertTrue(db.has_password(data['email'], data['password']))

    def testPostMessageWithBadType(self):
        data = SAMPLE_USER.copy()
        token = db.sign_in_user(data['email'])
        # Bad type on message.
        r = requests.post(URL + 'post_message', headers={'authorization': token}, json={
                          'email': SAMPLE_USER2['email'], 'message': 1337})
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data has incorrect type.')

    def testPostMessageWithBadData(self):
        # Don't supply message.
        r = requests.post(URL + 'post_message',
                          json={'email': SAMPLE_USER2['email']})
        data, code = r.json()
        self.assertEqual(code, 400)
        self.assertEqual(data['message'], 'Form data missing.')
