from sqlalchemy import text
from extensions import db


class PromotionRepository:

    @staticmethod
    def get_active_promotions():

        sql = """
        SELECT *
        FROM promotions
        WHERE is_active = true
        AND (starts_at IS NULL OR starts_at <= NOW())
        AND (ends_at IS NULL OR ends_at >= NOW())
        """

        return db.session.execute(text(sql)).mappings().all()


    @staticmethod
    def get_promotion_usage(promotion_id):

        sql = """
        SELECT COUNT(*)
        FROM promotion_redemptions
        WHERE promotion_id = :promotion_id
        """

        return db.session.execute(
            text(sql),
            {"promotion_id": promotion_id}
        ).scalar()