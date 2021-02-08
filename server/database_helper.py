import sqlite3
from sqlite3 import Error
import os.path

from utlis import generate_token

DATABASE = 'database.db'
SCHEMA = 'schema.sql'


def get_path_for(file):
    """ Returns the absolute path for the given file. """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(BASE_DIR, file)


def create_db():
    """ Initializes the database from the schema. """
    conn = None
    try:
        conn = sqlite3.connect(get_path_for(DATABASE))
        sql_file = open(get_path_for(SCHEMA))
        schema_str = sql_file.read()
        conn.executescript(schema_str)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def query(query, *args):
    """ Executes the given query. """
    query_with_factory(lambda res: None, sqlite3.Row, query, *args)


def query_and_process(process_result, query, *args):
    """
    Executes the given query and returns the results after being processed with
    the given function.
    """
    return query_with_factory(process_result, sqlite3.Row, query, *args)


def query_with_factory(process_result, factory, query, *args):
    """
    Executes the given query which returns results using the given factory.
    The query result is then processed with the given function and returned.
    """
    conn = None
    res = None
    try:
        conn = sqlite3.connect(get_path_for(DATABASE))
        conn.row_factory = factory
        query_res = conn.execute(query, args).fetchall()
        conn.commit()
        res = process_result(query_res)
    except Error as e:
        print(e)
        raise Exception(e)
    finally:
        if conn:
            conn.close()
        return res


def user_exists(email):
    """ Returns if there exists a user with the given email. """
    return query_and_process(lambda res: len(res) > 0,
                             'SELECT * FROM users WHERE email = ?', email)


def create_user(email, password, firstname, familyname, gender, city, country):
    """ Creates a user with the given information. """
    query('INSERT INTO users VALUES (?,?,?,?,?,?,?)', email,
          password, firstname, familyname, gender, city, country,)


def is_authorized(email, password):
    """ Returns whether there's a user with the given email and password. """
    return query_and_process(lambda res: len(res) > 0,
                             'SELECT * FROM users WHERE email = ? AND psw = ?', email, password)


def sign_in_user(email):
    """
    Signs in the given user and gives it a token.
    """
    token = generate_token()
    query('INSERT INTO tokens VALUES (?, ?)', email, token)
    return token


def token_exists(token):
    """ Returns whether token exists. """
    return query_and_process(lambda res: len(res) > 0,
                             'SELECT * FROM tokens WHERE token = ?', token)


def delete_token(token):
    """ Deletes the given token. """
    query('DELETE FROM tokens WHERE token = ?', token)


def get_user_by_token(token):
    """ Returns the primary key (email) of the user with the given token. """
    return query_and_process(lambda res: res[0][0] if res else None, 'SELECT email FROM tokens WHERE token = ?', token)


def has_password(email, password):
    """ Returns if the user with the given email has the given password. """
    return query_and_process(lambda res: len(res) > 0, 'SELECT * FROM users WHERE email = ? AND psw = ?', email, password)


def set_password(email, password):
    """ Updates the password of the given user. """
    query('UPDATE users SET psw = ? WHERE email = ?',
          password, email)


def user_exists(email):
    """ Returns whether a user with the given email exists. """
    return query_and_process(lambda res: len(res) > 0,
                             'SELECT * FROM users WHERE email = ?', email)


def user_factory(cursor, row):
    """
    Factory for creating a dictionary for a user without private information.
    """
    user = {}
    for idx, col in enumerate(cursor.description):
        if col[0] == 'psw' or col[0] == 'token':
            continue
        user[col[0]] = row[idx]
    return user


def get_user_data_by_email(email):
    """ Returns user data for the user with the given email. """
    return query_with_factory(
        lambda res: res[0] if res else None, user_factory, 'SELECT * FROM users WHERE email = ?', email)


def message_factory(cursor, row):
    """ Factory for creating a message. """
    message = {}
    for idx, col in enumerate(cursor.description):
        message[col[0]] = row[idx]
    return message


def get_user_messages_by_email(email):
    """ Returns messages for the user with the given email. """
    return query_with_factory(lambda res: res, message_factory, 'SELECT * FROM messages WHERE recipient = ?', email)


def post_message(writer, recipient, content):
    """ Posts the given message. """
    query('INSERT INTO messages (writer, recipient, content) VALUES (?, ?, ?)',
          writer, recipient, content)
