from repositories.WishlistRepository import WishlistRepository

class WishlistService:
    @staticmethod
    def get_wishlist_items(customer_id):

        wishlists = WishlistRepository.get_wishlists(customer_id)

        for wishlist in wishlists:
            print("Wishlist:", wishlist.title)

            for item in wishlist.items:
                print("  Item product_id:", item.product_id)
                
        return wishlists