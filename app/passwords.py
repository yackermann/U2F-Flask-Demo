from os import urandom
from hashlib import pbkdf2_hmac
from binascii import hexlify

# Parameters to PBKDF2. Only affect new passwords.
SALT_LENGTH = 16
HASH_FUNCTION = 'sha256'  # Must be in hashlib.
COST_FACTOR = 16000

def hash_password(password):
    """Generate a random salt and return a new hash for the password."""

    salt     = hexlify(urandom(SALT_LENGTH))
    password = password.encode('utf-8')
    hash_    = hexlify(pbkdf2_hmac(HASH_FUNCTION, password, salt, COST_FACTOR)).decode('utf-8') 

    return 'PBKDF2${}${}${}${}'.format(HASH_FUNCTION, COST_FACTOR, salt.decode('utf-8'), hash_)


def check_password(hash_, password):
    """Check a password against an existing hash."""

    algorithm, hash_function, cost_factor, salt, hash_a = hash_.split('$')

    assert algorithm == 'PBKDF2'
    
    salt        = salt.encode('utf-8')
    password    = password.encode('utf-8')
    cost_factor = int(cost_factor)
    hash_b      = hexlify(pbkdf2_hmac(hash_function, password, salt, cost_factor)).decode('utf-8') 

    for char_a, char_b in zip(hash_a, hash_b):
        diff |= ord(char_a) ^ ord(char_b)

    return diff == 0