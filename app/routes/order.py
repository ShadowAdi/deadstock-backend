from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth import get_current_user, require_buyer, require_seller
from service.order_service import order_service
from schemas.order import (
    CreateOrderRequest,
    OrderResponse,
    OrdersResponse,
    OrderData,
    OrderWithListingData
)
from schemas.base import BaseResponse
from models.User import User

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    data:  CreateOrderRequest,
    buyer: User    = Depends(require_buyer),
    db:    Session = Depends(get_db)
):
    order = order_service.create_order(db, buyer, data)
    return OrderResponse(
        success = True,
        message = "Order placed successfully",
        data    = OrderData.model_validate(order)
    )

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id:     str,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    order = order_service.get_order_by_id(db, order_id, current_user)
    return OrderResponse(
        success = True,
        message = "Order fetched",
        data    = OrderData.model_validate(order)
    )

@router.get("/buyer/my-orders", response_model=OrdersResponse)
def get_my_orders_as_buyer(
    buyer: User    = Depends(require_buyer),
    db:    Session = Depends(get_db)
):
    orders = order_service.get_buyer_orders(db, buyer)
    return OrdersResponse(
        success = True,
        message = f"{len(orders)} orders found",
        data    = [
            OrderWithListingData(
                **OrderData.model_validate(o).model_dump(),
                listing_title = o.listing.title,
                listing_city  = o.listing.city,
                seller_name   = o.listing.seller.business_name
            )
            for o in orders
        ]
    )

@router.get("/seller/received", response_model=OrdersResponse)
def get_received_orders_as_seller(
    seller: User    = Depends(require_seller),
    db:     Session = Depends(get_db)
):
    orders = order_service.get_seller_orders(db, seller)
    return OrdersResponse(
        success = True,
        message = f"{len(orders)} orders received",
        data    = [
            OrderWithListingData(
                **OrderData.model_validate(o).model_dump(),
                listing_title = o.listing.title,
                listing_city  = o.listing.city,
                seller_name   = seller.business_name
            )
            for o in orders
        ]
    )

@router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: str,
    buyer:    User    = Depends(require_buyer),
    db:       Session = Depends(get_db)
):
    order = order_service.cancel_order(db, order_id, buyer)
    return OrderResponse(
        success = True,
        message = "Order cancelled successfully",
        data    = OrderData.model_validate(order)
    )

@router.patch("/{order_id}/confirm", response_model=OrderResponse)
def confirm_order(
    order_id: str,
    seller:   User    = Depends(require_seller),
    db:       Session = Depends(get_db)
):
    order = order_service.confirm_order(db, order_id, seller)
    return OrderResponse(
        success = True,
        message = "Order confirmed",
        data    = OrderData.model_validate(order)
    )

@router.patch("/{order_id}/complete", response_model=OrderResponse)
def complete_order(
    order_id: str,
    seller:   User    = Depends(require_seller),
    db:       Session = Depends(get_db)
):
    order = order_service.complete_order(db, order_id, seller)
    return OrderResponse(
        success = True,
        message = "Order marked as completed",
        data    = OrderData.model_validate(order)
    )