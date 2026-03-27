from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from models.order import Order
from models.listings import Listing
from models.User import User
from schemas.order import CreateOrderRequest
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def create_order(self,db:Session,buyer:User,data:CreateOrderRequest)->Order:
        listing = db.query(Listing).filter(Listing.id == data.listing_id).first()
        if not listing:
            logger.error('Listing does not exist')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        if str(listing.seller_id) == str(buyer.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot place an order on your own listing"
            )
        
        if listing.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This listing is no longer available"
            )
        
        if data.quantity > listing.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {listing.quantity} units available"
            )

        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1"
            )
        
        total_price = listing.discount_price * data.quantity

        order = Order(
            buyer_id    = buyer.id,
            listing_id  = listing.id,
            quantity    = data.quantity,
            total_price = total_price,
            status      = "pending"
        )

        listing.quantity -= data.quantity

        if listing.quantity == 0:
            listing.status = "sold"
        
        db.add(order)
        db.commit()
        db.refresh(order)

        logger.info(f"Order {order.id} placed by buyer {buyer.id}")
        return order

    def get_order_by_id(self, db: Session, order_id: str, user: User) -> Order:
        order = (
            db.query(Order)
            .options(joinedload(Order.listing), joinedload(Order.buyer))
            .filter(Order.id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        is_buyer  = str(order.buyer_id)             == str(user.id)
        is_seller = str(order.listing.seller_id)    == str(user.id)

        if not is_buyer and not is_seller:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this order"
            )

        return order

    


