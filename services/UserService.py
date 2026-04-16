from extensions import db
from sqlalchemy import text
from repositories.UserRepository import UserRepository

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        user = UserRepository.get_customer_by_id(user_id)
        return user
    
    @staticmethod
    def add_phone_number(user_id, phone_number):
        user = UserRepository.get_customer_by_id(user_id)
        if not user:
            return "User not found"

        # Check if the phone number already exists for the user
        existing_phone = next((phone for phone in user.phone_numbers if phone.phone_number == phone_number), None)
        if existing_phone:
            return "Phone number already exists"

        # Add the new phone number to the user's list of phone numbers
        new_phone = UserRepository.add_phone_number(user_id, phone_number)
        return new_phone