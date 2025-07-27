from django.db import connection, transaction, IntegrityError, DatabaseError

from accounts.utils.logs import Logger

logger = Logger()


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

    def get_verified_user(self, email):
        q = """SELECT is_verified FROM users WHERE email = %s"""
        self.cursor.execute(q, [email])
        verified_user = self.cursor.fetchone()
        return verified_user[0] if verified_user else None

    def verify_user(self, user_id):
        q = """
        UPDATE users SET is_verified = 1 
        WHERE id = %s RETURNING id
        """
        self.cursor.execute(q, [user_id])
        user = self.cursor.fetchone()
        return user[0]

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

    def insert_refresh_token(self, user_id, token, expires):
        delete_q = """
            DELETE FROM refresh_tokens WHERE user_id = %s
        """
        insert_q = """
            INSERT INTO refresh_tokens (user_id, token, expires_at)
            VALUES (%s,%s,%s)
        """
        try:
            with transaction.atomic():
                self.cursor.execute(delete_q, [user_id])
                self.cursor.execute(insert_q, [user_id, token, expires])
                logger.log_info(f"refresh token for {user_id} inserted")
            return True
        except IntegrityError as e:
            logger.log_error(str(e))
            raise IntegrityError(f"Insert failed because of {e}")
        except DatabaseError as e:
            logger.log_error(str(e))
            raise DatabaseError(f"Insert failed because of {e}")
        except Exception as e:
            logger.log_error(str(e))
            raise Exception(str(e))

    def find_user_by_id_and_email(self, user_id, email):
        q = """
        SELECT id,email,username FROM users 
        WHERE id =%s AND email = %s LIMIT 1
        """
        self.cursor.execute(q, [user_id, email])

        row = self.cursor.fetchone()

        user = {}

        if row:
            user["user_id"] = row[0]
            user["email"] = row[1]
            user["username"] = row[2]

            return user
        return None
