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
    
    def get_buyer_orders(self, db: Session, buyer: User) -> list[Order]:
        orders = (
            db.query(Order)
            .options(joinedload(Order.listing).joinedload(Listing.seller))
            .filter(Order.buyer_id == buyer.id)
            .order_by(Order.created_at.desc())
            .all()
        )
        return orders
    
    def get_seller_orders(self, db: Session, seller: User) -> list[Order]:
        orders = (
            db.query(Order)
            .join(Listing, Order.listing_id == Listing.id)
            .options(joinedload(Order.listing), joinedload(Order.buyer))
            .filter(Listing.seller_id == seller.id)
            .order_by(Order.created_at.desc())
            .all()
        )
        return orders
    
    def cancel_order(self, db: Session, order_id: str, buyer: User) -> Order:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if str(order.buyer_id) != str(buyer.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own orders"
            )

        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel an order that is already {order.status}"
            )

        listing = db.query(Listing).filter(Listing.id == order.listing_id).first()
        if listing:
            listing.quantity += order.quantity
            if listing.status == "sold":       
                listing.status = "active"

        order.status = "cancelled"
        db.commit()
        db.refresh(order)

        logger.info(f"Order {order.id} cancelled by buyer {buyer.id}")
        return order
    
    def confirm_order(self, db: Session, order_id: str, seller: User) -> Order:
        order = (
            db.query(Order)
            .options(joinedload(Order.listing))
            .filter(Order.id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if str(order.listing.seller_id) != str(seller.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only confirm orders on your own listings"
            )

        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is already {order.status}"
            )

        order.status = "confirmed"
        db.commit()
        db.refresh(order)

        logger.info(f"Order {order.id} confirmed by seller {seller.id}")
        return order


    def complete_order(self, db: Session, order_id: str, seller: User) -> Order:
        order = (
            db.query(Order)
            .options(joinedload(Order.listing))
            .filter(Order.id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if str(order.listing.seller_id) != str(seller.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only complete orders on your own listings"
            )

        if order.status != "confirmed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order must be confirmed before marking complete"
            )

        order.status = "completed"
        db.commit()
        db.refresh(order)

        logger.info(f"Order {order.id} completed by seller {seller.id}")
        return order

order_service = OrderService()

