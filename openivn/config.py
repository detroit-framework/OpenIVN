"""OpenIVN development configuration."""
import os

# Root of application
APPLICATION_ROOT = '/'

# Database file path
DATABASE_FILENAME = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'var', 'openivn.sqlite3'
)


# Secret key is used to manage user sessions
# Set SECRET_KEY with: python3 -c "import os; print(os.urandom(24))"
SECRET_KEY = b'set secret key here'
# SESSION_COOKIE_NAME = 'login'
