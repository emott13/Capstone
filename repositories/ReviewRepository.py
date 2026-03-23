from sqlalchemy import text 
from sqlalchemy.sql import func
from extensions import db
from models import Reviews
import json

class ReviewRepository:
    """
    Creates an object with an array of Reviews objects. Can retrieve data
    with getReviews().
    """
    def __init__(self, product_id):
        self.product_id = product_id
        self.reviews = db.session.execute(
            db.select(Reviews).filter_by(product_id=product_id)
        ).fetchall()
        self.reviewCount = len(self.reviews)

        self.averageRating = self._initAverageRating()
        
        # dictionary containing the total of each star's reviews
        # ex two 1 star reviews, zero 2 stars, etc.
        self.ratingCount = self._initStarCount()

        # convert 2d array to 1d array
        self.reviews = [review[0] for review in self.reviews ]

    def getReviews(self):
        """Returns an array of Reviews objects"""
        return self.reviews
    
    def getReviewCount(self):
        return self.reviewCount
    
    def getAverageRating(self):
        return self.averageRating
    
    def getRatingCount(self, rating):
        """Returns the number of reviews with a certain star rating"""
        return self.ratingCount[rating]
    
    def getRatingPercent(self, rating):
        """Returns a number that's the percentage of total/rating"""
        ratingCount = self.getRatingCount(rating)

        if (ratingCount == 0):
            return 0

        return (ratingCount / self.reviewCount) * 100
    
    def getFullStars(self):
        """How many solid stars to show on the page"""
        return int(self.averageRating)

    def getHalfStars(self):
        """How many half stars to show on the page (0 or 1)"""
        return int(self.averageRating - int(self.averageRating) >= 0.7)

    def getEmptyStars(self):
        """How many empty stars to show on the page"""
        return 5 - self.getFullStars() - self.getHalfStars()
    
    # constructor helper function. Not meant for external usage
    def _initStarCount(self):
        starCount = {rating: 0 for rating in range(1, 6)}

        starQuery = db.session.query(
                Reviews.rating,
                func.count(Reviews.rating)
            ).filter_by(product_id=self.product_id).group_by(Reviews.rating).all()

        for query in starQuery:
            starCount[query[0]] = query[1]
        
        return starCount
    
    def _initAverageRating(self):
        if (self.reviewCount == 0):
            return 0

        return float(round(
            db.session.query(
                func.avg(Reviews.rating)
            ).filter(Reviews.product_id==self.product_id).scalar(),
            1))
