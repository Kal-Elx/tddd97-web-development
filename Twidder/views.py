from flask import jsonify, request
from Twidder import app

import Twidder.database.database_helper as db


@app.before_first_request
def init_server():
    """ Creates a new database according to schema.sql. """
    db.create_db()


@app.route('/', methods=["GET"])
def root():
    return app.send_static_file('client.html')


@app.route('/sign_up', methods=["POST"])
def sign_up():
    """
    Signs up a user with the supplied data if it's possible.
    Otherwise returns suitable error code and message.
    """
    data = request.get_json()
    if not ('email' in data and 'password' in data and 'firstname' in data and 'familyname' in data and 'gender' in data and 'city' in data and 'country' in data):
        return jsonify({'message': 'Form data missing.'}, 400)
    elif not (isinstance(data['email'], str) and isinstance(data['password'], str) and isinstance(data['firstname'], str) and isinstance(data['familyname'], str) and isinstance(data['gender'], str) and isinstance(data['city'], str) and isinstance(data['country'], str)):
        return jsonify({'message': 'Form data has incorrect type.'}, 400)
    elif db.user_exists(data['email']):
        return jsonify({'message': 'User already exists.'}, 204)
    elif len(data['password']) < 6:
        return jsonify({'message': 'Password is not long enough.'}, 204)
    elif len(data['password']) > 50:
        return jsonify({'message': 'Password is too long.'}, 204)

    try:
        db.create_user(data['email'], data['password'], data['firstname'],
                       data['familyname'], data['gender'], data['city'], data['country'])
        return jsonify({'message': 'Successfully created a new user.'}, 200)
    except:
        return jsonify(jsonify({'message': 'Something went wrong.'}, 500))


@app.route('/sign_in', methods=["POST"])
def sign_in():
    """
    Signs in a user with the supplied data if it's possible.
    Otherwise returns suitable error code and message.
    """
    data = request.get_json()
    if not ('email' in data and 'password' in data):
        return jsonify({'message': 'Form data missing.'}, 400)
    elif not (isinstance(data['email'], str) and isinstance(data['password'], str)):
        return jsonify({'message': 'Form data has incorrect type.'}, 400)
    elif not db.is_authorized(data['email'], data['password']):
        return jsonify({'message': 'Wrong username or password.'}, 401)

    token = db.sign_in_user(data['email'])
    return jsonify({'message': 'Successfully signed in.', 'data': token}, 200)


@app.route('/sign_out', methods=["POST"])
def sign_out():
    """ Signs out the user with the given token. """
    if not ('authorization' in request.headers):
        return jsonify({'message': 'Form data missing.'}, 400)
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not signed in.'}, 401)

    db.delete_token(request.headers.get('authorization'))
    return jsonify({'message': 'Successfully signed out.'}, 200)


@app.route('/change_password', methods=["POST"])
def change_password():
    """
    Changes to the new password for the user with the given token if the
    oldPassword is correct.
    """
    data = request.get_json()
    if not ('authorization' in request.headers and 'oldPassword' in data and 'newPassword' in data):
        return jsonify({'message': 'Form data missing.'}, 400)
    elif not (isinstance(data['oldPassword'], str) and isinstance(data['newPassword'], str)):
        return jsonify({'message': 'Form data has incorrect type.'}, 400)
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}, 401)
    elif len(data['newPassword']) < 6:
        return jsonify({'message': 'Password is not long enough.'}, 204)
    elif len(data['newPassword']) > 50:
        return jsonify({'message': 'Password is too long.'}, 204)

    user_email = db.get_user_by_token(request.headers.get('authorization'))
    if not db.has_password(user_email, data['oldPassword']):
        return jsonify({'message': 'Wrong password.'}, 401)

    db.set_password(user_email, data['newPassword'])
    return jsonify({'message': 'Password changed.'}, 200)


@app.route('/get_user_data_by_token', methods=["GET"])
def get_user_data_by_token():
    """ Returns the user data of the user with the given token. """
    if not ('authorization' in request.headers):
        return jsonify({'message': 'Form data missing.'}, 400)
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}, 401)

    user_email = db.get_user_by_token(request.headers.get('authorization'))
    user_data = db.get_user_data_by_email(user_email)
    return jsonify({'message': 'User data retrieved.', 'data': user_data}, 200)


@app.route('/get_user_data_by_email/<email>', methods=["GET"])
def get_user_data_by_email(email):
    """ Returns the user data of the user with the given token. """
    data = request.get_json()
    if not ('authorization' in request.headers):
        return jsonify({'message': 'Form data missing.'}, 400)
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}, 401)
    elif not db.user_exists(email):
        return jsonify({'message': 'No such user.'}, 204)

    user_data = db.get_user_data_by_email(email)
    return jsonify({'message': 'User data retrieved.', 'data': user_data}, 200)


@app.route('/get_user_messages_by_token', methods=["GET"])
def get_user_messages_by_token():
    """ Returns the messages of the user with the given token. """
    data = request.get_json()
    if not ('authorization' in request.headers):
        return jsonify({'message': 'Form data missing.'}, 400)
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}, 401)

    user_email = db.get_user_by_token(request.headers.get('authorization'))
    messages = db.get_user_messages_by_email(user_email)
    return jsonify({'message': 'User messages retrieved.', 'data': messages}, 200)


@app.route('/get_user_messages_by_email/<email>', methods=["GET"])
def get_user_messages_by_email(email):
    """ Returns the messages of the user with the given token. """
    if not 'authorization' in request.headers:
        return jsonify({'message': 'Form data missing.'}, 400)
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}, 401)
    elif not db.user_exists(email):
        return jsonify({'message': 'No such user.'}, 204)

    messages = db.get_user_messages_by_email(email)
    return jsonify({'message': 'User messages retrieved.', 'data': messages}, 200)


@app.route('/post_message', methods=["POST"])
def post_message():
    """ Posts a message on the wall of the user with the given email. """
    data = request.get_json()
    if not ('authorization' in request.headers and 'email' in data and 'message' in data):
        return jsonify({'message': 'Form data missing.'}, 400)
    elif not (isinstance(data['email'], str) and isinstance(data['message'], str)):
        return jsonify({'message': 'Form data has incorrect type.'}, 400)
    elif not db.token_exists(request.headers.get('authorization')):
        return jsonify({'message': 'You are not logged in.'}, 401)
    elif not db.user_exists(data['email']):
        return jsonify({'message': 'No such user.'}, 204)
    elif len(data['message']) > 500:
        return jsonify({'message': 'Message was too long.'}, 400)

    writer = db.get_user_by_token(request.headers.get('authorization'))
    db.post_message(writer, data['email'], data['message'])
    return jsonify({'message': 'Message posted.'}, 200)
