from datetime import datetime

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
import jwt

from accounts.repositories.user import UserRepository
from accounts.utils.utils import Utils
from accounts.utils.auth import JWTAuthentication
from accounts.utils.logs import Logger

logger = Logger()


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def get_by_mail(self, email) -> bool:
        user = self.user_repo.get_user_by_email(email)
        if not user[0]:
            return False
        return True

    def get_by_username(self, username) -> bool:
        user = self.user_repo.get_user_by_username(username)
        if not user[0]:
            return False
        return True

    def check_verified(self, email) -> bool:
        is_verified = self.user_repo.get_verified_user(email)
        if is_verified != 1:
            return False
        return True

    def verify(self, email) -> bool:
        verified = self.user_repo.verify_user(email)
        if verified != 1:
            return False
        return True

    def register_user(self, username, email, password) -> int:
        hashed_password = make_password(password)
        user = self.user_repo.create_user(username, email, hashed_password)
        if user < 1:
            return 0
        return user

    def create_session(self, email, password):
        user = self.user_repo.login_user(email)
        if not user:
            return ""
        id, username, email, is_verified, hashed_password = user

        if not check_password(password, hashed_password):
            return ""

        utils = Utils(user)

        access_tkn, refresh_tkn = utils.generate_tokens(id, email)

        return access_tkn, refresh_tkn

    def save_refresh_tkn(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "refresh":
                raise jwt.InvalidTokenError()
            user_id = payload.get("user_id")
            exp = datetime.fromtimestamp(payload.get("exp"))
        except jwt.ExpiredSignatureError:
            logger.log_error(jwt.ExpiredSignatureError)
            raise jwt.ExpiredSignatureError
        except jwt.InvalidTokenError:
            logger.log_error(jwt.InvalidTokenError)
            raise jwt.InvalidTokenError

        return self.user_repo.insert_refresh_token(user_id, token, exp)

    def refresh_tkn(self, user_id):
        refresh_tkn = self.user_repo.get_refresh_token(user_id)
        return refresh_tkn

    def logout(self, user_id):
        self.user_repo.delete_token(user_id)
