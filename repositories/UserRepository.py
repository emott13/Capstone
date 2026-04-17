from extensions import db
from sqlalchemy import text

class UserRepository:
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
    def add_phone_number(user_id, phone_number):
        sql = text("""
            INSERT INTO phone_numbers (user_id, phone_number)
            VALUES (:user_id, :phone_number)
            RETURNING phone_number_id
        """)
        
        result = db.session.execute(sql, {"user_id": user_id, "phone_number": phone_number}).fetchone()
        db.session.commit()
        return result