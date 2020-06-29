"""Generates API keys."""
import os
import hashlib


def generate_api_key():
    """Generates a new, securely random API key."""
    # Since output of SHA-512 is 512 bits, only need 64 bytes of random data
    num_bytes = 64
    tmp = os.urandom(num_bytes)
    return hashlib.sha512(tmp).hexdigest()


if __name__ == '__main__':
    print(generate_api_key())
