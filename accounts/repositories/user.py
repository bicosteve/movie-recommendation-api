from django.db import connection


class UserRepository:
    def __init__(self):
        self.cursor = connection.cursor()

    def get_user_by_email(self, email):
        q = """
        SELECT 1 FROM users WHERE email = %s
        """
        self.cursor.execute(q, [email])
        user = self.cursor.fetchone()
        return user

    def get_user_by_username(self, username):
        q = """
        SELECT 1 FROM users WHERE username = %s
        """
        self.cursor.execute(q, [username])
        user = self.cursor.fetchone()
        return user

    def get_verified_user(self, user_id):
        q = """SELECT is_verified FROM users WHERE id = %s"""
        self.cursor.execute(q, [user_id])
        user = self.cursor.fetchone()
        return user

    def verify_user(self, user_id):
        q = """
        UPDATE users SET is_verified = 1 
        WHERE id = %s RETURNING id
        """
        self.cursor.execute(q, [user_id])
        user = self.cursor.fetchone()
        return user

    def create_user(self, username, email, password):
        q = """
        INSERT INTO users (username,email,hashed_password) 
        VALUES (%s,%s,%s) RETURNING id;
        """
        self.cursor.execute(q, [username, email, password])

        user_id = self.cursor.fetchone()[0]

        return user_id

    def login_user(self, email):
        q = """
            SELECT id,username,email,is_verified,hashed_password
            FROM users WHERE email = %s
        """

        self.cursor.execute(q, [email])
        user = self.cursor.fetchone()

        if not user:
            return None
        return user

    def get_refresh_token(self, user_id):
        q = """
        SELECT token FROM refresh_tokens WHERE user_id = %s
        """
        self.cursor.execute(q, [user_id])
        result = self.cursor.fetchone()
        return result[0]

    def delete_token(self, user_id):
        q = """DELETE FROM refresh_tokens WHERE user_id = %s"""
        self.cursor.execute(q, [user_id])
