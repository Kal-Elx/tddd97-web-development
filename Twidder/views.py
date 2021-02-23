import os
import json
import http.client
import urllib.parse
from flask import jsonify, request
from geventwebsocket import WebSocketError
from Twidder import app

import Twidder.database.database_helper as db

# Active socket sessions.
sessions = dict()


@app.before_first_request
def init_server():
    """ Creates a new database according to schema.sql. """
    db.create_db()


@app.route('/', methods=["GET"])
def root():
    return app.send_static_file('client.html')


@app.route('/clean_db', methods=["GET"])
def clean_db():
    """
    Returns the home page and resets the database.
    NOTE: Only used for testing.
    """
    init_server()
    return root()


@app.route('/sign_up', methods=["POST"])
def sign_up():
    """
    Signs up a user with the supplied data if it's possible.
    Otherwise returns suitable error code and message.
    """
    data = request.get_json()
    if not ('email' in data and 'password' in data and 'firstname' in data and 'familyname' in data and 'gender' in data and 'city' in data and 'country' in data):
        return jsonify({'message': 'Form data missing.'}), 400
    elif not (isinstance(data['email'], str) and isinstance(data['password'], str) and isinstance(data['firstname'], str) and isinstance(data['familyname'], str) and isinstance(data['gender'], str) and isinstance(data['city'], str) and isinstance(data['country'], str)):
        return jsonify({'message': 'Form data has incorrect type.'}), 400
    elif db.user_exists(data['email']):
        return jsonify({'message': 'User already exists.'}), 409
    elif len(data['password']) < 6:
        return jsonify({'message': 'Password is not long enough.'}), 406
    elif len(data['password']) > 50:
        return jsonify({'message': 'Password is too long.'}), 406

    try:
        db.create_user(data['email'], data['password'], data['firstname'],
                       data['familyname'], data['gender'], data['city'], data['country'])
        return jsonify({'message': 'Successfully created a new user.'}), 200
    except:
        return jsonify({'message': 'Something went wrong.'}), 500


@app.route('/sign_in', methods=["POST"])
def sign_in():
    """
    Signs in a user with the supplied data if it's possible.
    Otherwise returns suitable error code and message.
    """
    data = request.get_json()
    if not ('email' in data and 'password' in data):
        return jsonify({'message': 'Form data missing.'}), 400
    elif not (isinstance(data['email'], str) and isinstance(data['password'], str)):
        return jsonify({'message': 'Form data has incorrect type.'}), 400
    elif not db.is_authorized(data['email'], data['password']):
        return jsonify({'message': 'Wrong username or password.'}), 401

    if db.is_signed_in(data['email']):
        old_token = db.get_token_by_email(data['email'])
        if old_token in sessions:
            sessions[old_token].send("signout")
        terminate_user_session(old_token)

    token = db.sign_in_user(data['email'])
    trigger_live_data_update()
    return jsonify({'message': 'Successfully signed in.', 'data': {'token': token}}), 200


@app.route('/sign_out', methods=["POST"])
def sign_out():
    """ Signs out the user with the given token. """
    if not ('authorization' in request.headers):
        return jsonify({'message': 'Form data missing.'}), 400
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not signed in.'}), 401

    terminate_user_session(request.headers.get('authorization'))
    trigger_live_data_update()
    return jsonify({'message': 'Successfully signed out.'}), 200


@app.route('/change_password', methods=["POST"])
def change_password():
    """
    Changes to the new password for the user with the given token if the
    oldPassword is correct.
    """
    data = request.get_json()
    if not ('authorization' in request.headers and 'oldPassword' in data and 'newPassword' in data):
        return jsonify({'message': 'Form data missing.'}), 400
    elif not (isinstance(data['oldPassword'], str) and isinstance(data['newPassword'], str)):
        return jsonify({'message': 'Form data has incorrect type.'}), 400
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}), 401
    elif len(data['newPassword']) < 6:
        return jsonify({'message': 'Password is not long enough.'}), 406
    elif len(data['newPassword']) > 50:
        return jsonify({'message': 'Password is too long.'}), 406

    user_email = db.get_user_by_token(request.headers.get('authorization'))
    if not db.has_password(user_email, data['oldPassword']):
        return jsonify({'message': 'Wrong password.'}), 401

    db.set_password(user_email, data['newPassword'])
    return jsonify({'message': 'Password changed.'}), 200


@app.route('/get_user_data_by_token', methods=["GET"])
def get_user_data_by_token():
    """ Returns the user data of the user with the given token. """
    if not ('authorization' in request.headers):
        return jsonify({'message': 'Form data missing.'}), 400
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}), 401

    user_email = db.get_user_by_token(request.headers.get('authorization'))
    user_data = db.get_user_data_by_email(user_email)
    return jsonify({'message': 'User data retrieved.', 'data': user_data}), 200


@app.route('/get_user_data_by_email/<email>', methods=["GET"])
def get_user_data_by_email(email):
    """ Returns the user data of the user with the given token. """
    if not ('authorization' in request.headers):
        return jsonify({'message': 'Form data missing.'}), 400
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}), 401
    elif not db.user_exists(email):
        return jsonify({'message': 'No such user.'}), 406

    user_data = db.get_user_data_by_email(email)
    return jsonify({'message': 'User data retrieved.', 'data': user_data}), 200


@app.route('/get_user_messages_by_token', methods=["GET"])
def get_user_messages_by_token():
    """ Returns the messages of the user with the given token. """
    if not ('authorization' in request.headers):
        return jsonify({'message': 'Form data missing.'}), 400
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}), 401

    user_email = db.get_user_by_token(request.headers.get('authorization'))
    messages = db.get_user_messages_by_email(user_email)
    return jsonify({'message': 'User messages retrieved.', 'data': messages}), 200


@app.route('/get_user_messages_by_email/<email>', methods=["GET"])
def get_user_messages_by_email(email):
    """ Returns the messages of the user with the given token. """
    if not 'authorization' in request.headers:
        return jsonify({'message': 'Form data missing.'}), 400
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}), 401
    elif not db.user_exists(email):
        return jsonify({'message': 'No such user.'}), 406

    messages = db.get_user_messages_by_email(email)
    return jsonify({'message': 'User messages retrieved.', 'data': messages}), 200


@app.route('/post_message', methods=["POST"])
def post_message():
    """ Posts a message on the wall of the user with the given email. """
    data = request.get_json()
    if not ('authorization' in request.headers and 'email' in data and 'message' in data and 'latitude' in data and 'longitude' in data):
        return jsonify({'message': 'Form data missing.'}), 400
    elif not (isinstance(data['email'], str) and isinstance(data['message'], str) and data['latitude'], str) and isinstance(data['longitude'], str):
        return jsonify({'message': 'Form data has incorrect type.'}), 400
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}), 401
    elif not db.user_exists(data['email']):
        return jsonify({'message': 'No such user.'}), 409
    elif len(data['message']) > 500:
        return jsonify({'message': 'Message was too long.'}), 406

    writer = db.get_user_by_token(request.headers.get('authorization'))
    db.post_message(writer, data['email'], data['message'], get_location(
        data['latitude'], data['longitude']))
    trigger_live_data_update()
    return jsonify({'message': 'Message posted.'}), 200


@app.route('/new_session', methods=["GET"])
def new_session():
    """
    Sets up a new session which is closed when a user signs out or signs in on
    another browser.
    """
    ws = request.environ.get('wsgi.websocket')

    if not ws:
        return jsonify({'message': 'Expected WebSocket request.'}), 400

    try:
        while True:
            # Wait for client to send token.
            token = ws.receive()

            if token is not None:
                # Store handle to session.
                sessions[token] = ws

                # Send Twidder Statistics to newly signed in user.
                ws.send(get_twidder_statistics())

    except WebSocketError:
        # Do nothing. This happens when the socket is closed.
        pass

    return ''


def terminate_user_session(token):
    """ Handle terminating a user session. """
    db.delete_token(token)

    # Terminate the user's ongoing sessions.
    if token in sessions:
        sessions[token].close()


def trigger_live_data_update():
    """
    Updates the Twidder statistics chart for all active users and removes
    closed sockets from active sessions.
    """
    closed_sessions = []
    for token, ws in sessions.items():
        try:
            ws.send(get_twidder_statistics())
        except WebSocketError:
            if ws.closed:
                # Clean up sessions that weren't closed properly.
                closed_sessions.append(token)

    for token in closed_sessions:
        del sessions[token]


def get_twidder_statistics():
    """ Returns Twidder Statistics as JSON. """
    return json.dumps([
        db.get_number_of_active_users(),
        db.get_number_of_sent_messages(),
        db.get_number_of_nationalities(),
    ])


def get_location(lat, lon):
    API_KEY = get_geocode_api_key()
    conn = http.client.HTTPConnection('geocode.xyz')

    params = urllib.parse.urlencode({
        'auth': API_KEY,
        'locate': '{},{}'.format(lat, lon),
        'region': 'SE',
        'json': 1,
    })

    conn.request('GET', '/?{}'.format(params))

    res = conn.getresponse()
    data = res.read()

    data = json.loads(data.decode('utf-8'))

    res = ''
    if 'country' in data:
        res = data['country']
        if 'city' in data:
            res = '{}, {}'.format(data['city'], res)

    return res if res is not None else 'Unknown location'


def get_geocode_api_key():
    key_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '..', 'geocode_api_key.txt')
    key = ''
    with open(key_path) as f:
        key = f.readlines()
    return key
