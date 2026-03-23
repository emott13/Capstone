from extensions import db
from sqlalchemy import text

class UserRepository: 
    @staticmethod
    def get_user_by_id(user_id):
        
        sql = """
        SELECT user_id, username, email, created_at
        FROM users
        WHERE user_id = :user_id
        """

        result = db.session.execute(
            text(sql),
            {"user_id": user_id}
        ).fetchone()

        if result:
            return {
                "user_id": result[0],
                "username": result[1],
                "email": result[2],
                "created_at": result[3]
            }
        else:
            return None