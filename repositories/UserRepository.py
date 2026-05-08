from extensions import db
from sqlalchemy import text
from models import Users, PhoneNumbers

class UserRepository:
    @staticmethod
    def get_user_by_id(user_id) -> Users:
        return Users.query.where(Users.user_id == user_id).one_or_none()

    @staticmethod
    def get_customer_by_id(user_id):
        sql = text("""
            SELECT *
            FROM users
            WHERE user_id = :user_id
        """)
        
        result = db.session.execute(sql, {"user_id": user_id}).fetchone()
        if result:
            return {
                "username": result[0],
                "email": result[1],
                "created_at": result[2]
            }

    @staticmethod
    def add_phone_number(user: Users, phone_number: str):
        # sql = text("""
        #     INSERT INTO phone_numbers (user_id, phone_number)
        #     VALUES (:user_id, :phone_number)
        #     RETURNING phone_number_id
        # """)
        
        # result = db.session.execute(sql, {"user_id": user_id, "phone_number": phone_number}).fetchone()

        phone_number_model = PhoneNumbers.query \
            .where(PhoneNumbers.phone_number == phone_number).one_or_none()

        if not phone_number_model:
            phone_number_model = PhoneNumbers(phone_number=phone_number)

        user.phone_numbers.append(phone_number_model)

        db.session.commit()