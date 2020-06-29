"""Custom User class which inherits from the flask_login UserMixin class."""

from flask_login import UserMixin
from openivn.model import get_db


class User(UserMixin):
    """User class, see https://realpython.com/flask-google-login/ for more."""
    def __init__(self, id_in, name_in, email_in):
        self.id = id_in
        self.name = name_in
        self.email = email_in

    @staticmethod
    def get(user_id):
        """Get user from DB by ID, returns None if not found."""
        # Set up cursor to access database
        cursor = get_db().cursor()

        # Retrieve user by ID
        user = cursor.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        # Check to ensure user is in DB
        if not user:
            return None

        user = User(
            id_in=user['id'],
            name_in=user['name'],
            email_in=user['email']
        )

        return user

    @staticmethod
    def add(user_id, name, email):
        """Add user to DB."""
        # Set up access to database
        db = get_db()
        db.execute(
            "INSERT INTO users(id, name, email) "
            "VALUES (?, ?, ?)",
            (user_id, name, email),
        )
        db.commit()
