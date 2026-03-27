from extensions import db
from sqlalchemy import text
from repositories.UserRepository import UserRepository

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        user = UserRepository.get_customer_by_id(user_id)
        return user