from extensions import db
from sqlalchemy import text

class UserRepository:
    @staticmethod
    def get_customer_by_id(user_id):
        sql = text("""
            SELECT username, email, created_at
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
