import random
import string

TOKEN_LENGTH = 36


def generate_token():
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(TOKEN_LENGTH))
