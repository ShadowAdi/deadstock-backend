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