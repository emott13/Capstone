from repositories.WishlistRepository import WishlistRepository
from extensions import db

class WishlistService:
    @staticmethod
    def get_wishlist_items(customer_id):

        wishlists = WishlistRepository.get_wishlists(customer_id)

        for wishlist in wishlists:
            for item in wishlist.items:
                if item.product:
                    item.subtotal = item.product.price * item.quantity
                else:
                    item.subtotal = 0
                
        return wishlists
    
    @staticmethod
    def update_quantities(customer_id, form_data):
        print('start')

        for field, value in form_data.items():

            print('field: ', field, ' and value: ', value)

            if field.startswith("quantity_"):
                print('field!')

                wishlist_item_id = int(field.replace("quantity_", ""))
                quantity = int(value)

                if quantity <= 0:
                    WishlistRepository.remove_item(wishlist_item_id)
                else:
                    print(f"Item ID: {wishlist_item_id}, Quantity: {quantity}") # debug print
                    WishlistRepository.update_quantity(
                        wishlist_item_id,
                        quantity
                    )

        db.session.commit()
        

        return WishlistService.calculate_total(customer_id)


    @staticmethod
    def calculate_total(customer_id):
        wishlists = WishlistRepository.get_wishlists(customer_id)

        total = 0

        for wishlist in wishlists:
            for item in wishlist.items:
                if item.product:
                    subtotal = item.product.price * item.quantity
                    total += subtotal

        return total

    @staticmethod
    def remove_item(wishlist_item_id):
        
        WishlistRepository.remove_item(wishlist_item_id)
        db.session.commit()