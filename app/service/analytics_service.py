from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models.listings import Listing
from models.order import Order
from models.User import User
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def get_trending_categories(self,db:Session)->list[dict]:
        results=(
            db.query(
                Listing.category,
                func.count(Order.id).label("total_orders"),
                func.sum(Order.quantity).label("total_units_sold"),
                func.sum(Order.total_price).label("total_revenue"),
            ).join(Order,Order.listing_id==Listing.id).filter(Order.status.in_(["confirmed", "completed"])).group_by(Listing.category).order_by(desc("total_orders")).limit(10).all()
        )
        
        return [
            {
                "category":        row.category,
                "total_orders":    row.total_orders,
                "total_units_sold": int(row.total_units_sold or 0),
                "total_revenue":   round(float(row.total_revenue or 0), 2),
            }
            for row in results
        ]
    
    def get_total_savings(self, db: Session) -> dict:
        completed = (
            db.query(func.sum(Order.total_price))
            .filter(Order.status.in_(["confirmed", "completed"]))
            .scalar() or 0
        )
        
        original_value = (
            db.query(
                func.sum(Listing.original_price * Order.quantity)
            )
            .join(Order, Order.listing_id == Listing.id)
            .filter(Order.status.in_(["confirmed", "completed"]))
            .scalar() or 0
        )

        total_saved     = original_value - completed
        total_orders    = db.query(func.count(Order.id)).filter(
            Order.status.in_(["confirmed", "completed"])
        ).scalar() or 0
        total_listings  = db.query(func.count(Listing.id)).scalar() or 0
        active_listings = db.query(func.count(Listing.id)).filter(
            Listing.status == "active"
        ).scalar() or 0

        return {
            "total_saved_inr":       round(float(total_saved), 2),
            "total_traded_value_inr": round(float(completed), 2),
            "original_value_inr":    round(float(original_value), 2),
            "total_orders_completed": int(total_orders),
            "total_listings":        int(total_listings),
            "active_listings":       int(active_listings),
            "avg_discount_pct":      round(
                (float(total_saved) / float(original_value) * 100)
                if original_value > 0 else 0,
                2
            ),
        }