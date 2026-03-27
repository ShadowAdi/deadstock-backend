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
        
    def get_seller_dashboard(self, db: Session, seller: User) -> dict:

        listing_stats = (
            db.query(
                Listing.status,
                func.count(Listing.id).label("count")
            )
            .filter(Listing.seller_id == seller.id)
            .group_by(Listing.status)
            .all()
        )

        listings_by_status = {row.status: row.count for row in listing_stats}

        order_stats = (
            db.query(
                Order.status,
                func.count(Order.id).label("count"),
                func.sum(Order.total_price).label("revenue")
            )
            .join(Listing, Order.listing_id == Listing.id)
            .filter(Listing.seller_id == seller.id)
            .group_by(Order.status)
            .all()
        )

        orders_by_status = {
            row.status: {
                "count":   row.count,
                "revenue": round(float(row.revenue or 0), 2)
            }
            for row in order_stats
        }

        total_revenue = sum(
            v["revenue"]
            for k, v in orders_by_status.items()
            if k in ("confirmed", "completed")
        )

        total_units_sold = (
            db.query(func.sum(Order.quantity))
            .join(Listing, Order.listing_id == Listing.id)
            .filter(
                Listing.seller_id == seller.id,
                Order.status.in_(["confirmed", "completed"])
            )
            .scalar() or 0
        )

        original_val = (
            db.query(func.sum(Listing.original_price * Order.quantity))
            .join(Order, Order.listing_id == Listing.id)
            .filter(
                Listing.seller_id == seller.id,
                Order.status.in_(["confirmed", "completed"])
            )
            .scalar() or 0
        )

        value_rescued = float(original_val) - total_revenue

        top_listing = (
            db.query(
                Listing.title,
                func.sum(Order.total_price).label("revenue"),
                func.sum(Order.quantity).label("units")
            )
            .join(Order, Order.listing_id == Listing.id)
            .filter(
                Listing.seller_id == seller.id,
                Order.status.in_(["confirmed", "completed"])
            )
            .group_by(Listing.title)
            .order_by(desc("revenue"))
            .first()
        )

        return {
            "seller": {
                "id":            str(seller.id),
                "business_name": seller.business_name,
                "city":          seller.city,
            },
            "listings": {
                "active":  listings_by_status.get("active",  0),
                "sold":    listings_by_status.get("sold",    0),
                "closed":  listings_by_status.get("closed",  0),
                "total":   sum(listings_by_status.values()),
            },
            "orders": {
                "pending":   orders_by_status.get("pending",   {}).get("count", 0),
                "confirmed": orders_by_status.get("confirmed", {}).get("count", 0),
                "completed": orders_by_status.get("completed", {}).get("count", 0),
                "cancelled": orders_by_status.get("cancelled", {}).get("count", 0),
            },
            "financials": {
                "total_revenue_inr":  round(total_revenue, 2),
                "total_units_sold":   int(total_units_sold),
                "original_value_inr": round(float(original_val), 2),
                "value_rescued_inr":  round(value_rescued, 2),
            },
            "top_listing": {
                "title":   top_listing.title   if top_listing else None,
                "revenue": round(float(top_listing.revenue), 2) if top_listing else 0,
                "units":   int(top_listing.units)               if top_listing else 0,
            }
        }