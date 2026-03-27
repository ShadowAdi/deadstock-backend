# Dead Inventory Marketplace — API Documentation

A B2B marketplace API where MSMEs can offload excess/dead inventory to resellers and small shops at discounted prices.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Auth & User APIs](#auth--user-apis)
- [Listing APIs](#listing-apis)
- [Order APIs](#order-apis)
- [Analytics APIs](#analytics-apis)
- [Error Codes](#error-codes)

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+

### Run with Docker

```bash
git clone https://github.com/your-repo/dead-inventory
cd dead-inventory
cp .env.example .env
docker-compose up --build
```

### Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Environment Variables

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/dead_inventory
SECRET_KEY=your-very-long-secret-key-here
```

### Interactive Docs

Once running, visit:
- Swagger UI → `http://localhost:8000/docs`
- ReDoc → `http://localhost:8000/redoc`

---

## Base URL

```
http://localhost:8000
```

---

## Authentication

This API uses **JWT Bearer tokens**.

After login, include the token in every protected request:

```
Authorization: Bearer <your_access_token>
```

Tokens expire in **24 hours**.

### Roles

| Role | Description |
|---|---|
| `seller` | MSMEs uploading dead inventory |
| `buyer` | Resellers/shops purchasing bulk stock |

---

## Response Format

Every response follows this structure:

### Success

```json
{
  "success": true,
  "message": "Human readable message",
  "data": { }
}
```

### Failure

```json
{
  "success": false,
  "message": "What went wrong",
  "data": null
}
```

---

## Auth & User APIs

### POST `/auth/register`

Register a new seller or buyer account.

**Auth required:** No

**Request body:**

```json
{
  "email": "shop@example.com",
  "password": "secret123",
  "role": "seller",
  "business_name": "Rahul Garments",
  "city": "Lucknow",
  "phone": "9876543210"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `email` | string | ✅ | Must be unique |
| `password` | string | ✅ | Min 6 characters |
| `role` | string | ✅ | `seller` or `buyer` |
| `business_name` | string | ✅ | |
| `city` | string | ✅ | |
| `phone` | string | ✅ | |

**Success response `201`:**

```json
{
  "success": true,
  "message": "Account created successfully",
  "data": {
    "id": "uuid",
    "email": "shop@example.com",
    "role": "seller",
    "business_name": "Rahul Garments",
    "city": "Lucknow",
    "phone": "9876543210",
    "created_at": "2024-03-01T10:00:00"
  }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `400` | Email already registered |
| `400` | Password must be at least 6 characters |

---

### POST `/auth/login`

Login and receive an access token.

**Auth required:** No

**Request body:**

```json
{
  "email": "shop@example.com",
  "password": "secret123"
}
```

**Success response `200`:**

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "shop@example.com",
      "role": "seller",
      "business_name": "Rahul Garments",
      "city": "Lucknow",
      "phone": "9876543210",
      "created_at": "2024-03-01T10:00:00"
    }
  }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `401` | Invalid email or password |

---

### GET `/auth/me`

Get the currently logged-in user's profile.

**Auth required:** Yes (any role)

**Success response `200`:**

```json
{
  "success": true,
  "message": "Profile fetched",
  "data": {
    "id": "uuid",
    "email": "shop@example.com",
    "role": "seller",
    "business_name": "Rahul Garments",
    "city": "Lucknow",
    "phone": "9876543210",
    "created_at": "2024-03-01T10:00:00"
  }
}
```

---

### PUT `/auth/me`

Update own profile details.

**Auth required:** Yes (any role)

**Request body** (all fields optional):

```json
{
  "business_name": "Rahul Traders",
  "city": "Kanpur",
  "phone": "9123456789"
}
```

**Success response `200`:**

```json
{
  "success": true,
  "message": "Profile updated",
  "data": { ...updated user object }
}
```

---

### PUT `/auth/me/password`

Change account password.

**Auth required:** Yes (any role)

**Request body:**

```json
{
  "old_password": "secret123",
  "new_password": "newpassword456"
}
```

**Success response `200`:**

```json
{
  "success": true,
  "message": "Password changed successfully",
  "data": null
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `400` | Current password is incorrect |
| `400` | New password must be at least 6 characters |

---

### GET `/auth/seller/{seller_id}`

View a seller's public profile. Buyers use this before placing an order.

**Auth required:** No

**Success response `200`:**

```json
{
  "success": true,
  "message": "Seller profile fetched",
  "data": {
    "seller": {
      "id": "uuid",
      "business_name": "Rahul Garments",
      "city": "Lucknow",
      "role": "seller"
    },
    "listings_count": 12
  }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `404` | Seller not found |

---

## Listing APIs

### POST `/listings/`

Create a new dead inventory listing.

**Auth required:** Yes — `seller` only

**Request body:**

```json
{
  "title": "Winter Jackets — Bulk Lot",
  "description": "500 unsold winter jackets from last season, good condition",
  "category": "Clothing",
  "quantity": 500,
  "original_price": 1200.00,
  "discount_price": 400.00,
  "city": "Lucknow"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | ✅ | |
| `description` | string | ❌ | |
| `category` | string | ✅ | |
| `quantity` | int | ✅ | Must be > 0 |
| `original_price` | float | ✅ | Must be > 0 |
| `discount_price` | float | ✅ | Must be < original_price |
| `city` | string | ✅ | |

**Success response `201`:**

```json
{
  "success": true,
  "message": "Listing created successfully",
  "data": {
    "id": "uuid",
    "seller_id": "uuid",
    "title": "Winter Jackets — Bulk Lot",
    "description": "500 unsold winter jackets from last season",
    "category": "Clothing",
    "quantity": 500,
    "original_price": 1200.00,
    "discount_price": 400.00,
    "discount_pct": 66.67,
    "city": "Lucknow",
    "status": "active",
    "created_at": "2024-03-01T10:00:00"
  }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `400` | Discount price must be lower than original price |
| `400` | Quantity must be at least 1 |
| `403` | Only sellers can perform this action |

---

### GET `/listings/search`

Search and filter all active listings. Public endpoint.

**Auth required:** No

**Query parameters:**

| Param | Type | Required | Notes |
|---|---|---|---|
| `q` | string | ❌ | Keyword search in title/description |
| `category` | string | ❌ | Filter by category |
| `city` | string | ❌ | Filter by city |
| `min_price` | float | ❌ | Min discount price |
| `max_price` | float | ❌ | Max discount price |
| `page` | int | ❌ | Default: 1 |
| `page_size` | int | ❌ | Default: 20, Max: 100 |

**Example request:**

```
GET /listings/search?q=jacket&city=lucknow&max_price=500&page=1
```

**Success response `200`:**

```json
{
  "success": true,
  "message": "4 listings found",
  "data": {
    "listings": [ ...array of listing objects ],
    "pagination": {
      "total": 4,
      "page": 1,
      "page_size": 20,
      "pages": 1
    }
  }
}
```

---

### GET `/listings/nearby`

Get active listings in a specific city.

**Auth required:** No

**Query parameters:**

| Param | Type | Required |
|---|---|---|
| `city` | string | ✅ |

**Example request:**

```
GET /listings/nearby?city=Lucknow
```

**Success response `200`:**

```json
{
  "success": true,
  "message": "8 listings near Lucknow",
  "data": [ ...array of listing objects ]
}
```

---

### GET `/listings/category/{category}`

Get all active listings under a specific category.

**Auth required:** No

**Example request:**

```
GET /listings/category/Clothing
```

**Success response `200`:**

```json
{
  "success": true,
  "message": "15 listings in Clothing",
  "data": [ ...array of listing objects ]
}
```

---

### GET `/listings/mine`

Get all listings created by the logged-in seller.

**Auth required:** Yes — `seller` only

**Query parameters:**

| Param | Type | Required | Notes |
|---|---|---|---|
| `status` | string | ❌ | Filter: `active`, `sold`, `closed` |

**Example request:**

```
GET /listings/mine?status=active
```

**Success response `200`:**

```json
{
  "success": true,
  "message": "3 listings found",
  "data": [ ...array of listing objects ]
}
```

---

### GET `/listings/{listing_id}`

Get a single listing by ID. Public endpoint.

**Auth required:** No

**Success response `200`:**

```json
{
  "success": true,
  "message": "Listing fetched",
  "data": {
    "id": "uuid",
    "seller_id": "uuid",
    "title": "Winter Jackets — Bulk Lot",
    "category": "Clothing",
    "quantity": 500,
    "original_price": 1200.00,
    "discount_price": 400.00,
    "discount_pct": 66.67,
    "city": "Lucknow",
    "status": "active",
    "created_at": "2024-03-01T10:00:00"
  }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `404` | Listing not found |

---

### PUT `/listings/{listing_id}`

Update a listing. Only the owner seller can edit.

**Auth required:** Yes — `seller` only

**Request body** (all fields optional):

```json
{
  "title": "Winter Jackets — Final Clearance",
  "quantity": 450,
  "discount_price": 350.00,
  "status": "active"
}
```

**Success response `200`:**

```json
{
  "success": true,
  "message": "Listing updated",
  "data": { ...updated listing object }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `400` | Cannot edit a listing that is already sold |
| `400` | Discount price must be lower than original price |
| `403` | You can only edit your own listings |
| `404` | Listing not found |

---

### DELETE `/listings/{listing_id}`

Delete a listing. If orders exist on it, it gets soft-closed instead of hard deleted.

**Auth required:** Yes — `seller` only

**Success response `200`:**

```json
{
  "success": true,
  "message": "Listing deleted"
}
```

or if orders exist:

```json
{
  "success": true,
  "message": "Listing closed (has existing orders)"
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `403` | You can only delete your own listings |
| `404` | Listing not found |

---

## Order APIs

### POST `/orders/`

Place an order on a listing.

**Auth required:** Yes — `buyer` only

**Request body:**

```json
{
  "listing_id": "uuid",
  "quantity": 50
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `listing_id` | UUID | ✅ | Must be an active listing |
| `quantity` | int | ✅ | Cannot exceed available stock |

**Success response `201`:**

```json
{
  "success": true,
  "message": "Order placed successfully",
  "data": {
    "id": "uuid",
    "buyer_id": "uuid",
    "listing_id": "uuid",
    "quantity": 50,
    "total_price": 20000.00,
    "status": "pending",
    "created_at": "2024-03-01T10:00:00"
  }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `400` | You cannot place an order on your own listing |
| `400` | This listing is no longer available |
| `400` | Only {n} units available |
| `400` | Quantity must be at least 1 |
| `403` | Only buyers can perform this action |
| `404` | Listing not found |

---

### GET `/orders/{order_id}`

Get a single order by ID. Both buyer (their own) and seller (on their listings) can access.

**Auth required:** Yes (any role)

**Success response `200`:**

```json
{
  "success": true,
  "message": "Order fetched",
  "data": {
    "id": "uuid",
    "buyer_id": "uuid",
    "listing_id": "uuid",
    "quantity": 50,
    "total_price": 20000.00,
    "status": "pending",
    "created_at": "2024-03-01T10:00:00"
  }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `403` | You don't have access to this order |
| `404` | Order not found |

---

### GET `/orders/buyer/my-orders`

Get all orders placed by the logged-in buyer, with listing details.

**Auth required:** Yes — `buyer` only

**Success response `200`:**

```json
{
  "success": true,
  "message": "3 orders found",
  "data": [
    {
      "id": "uuid",
      "buyer_id": "uuid",
      "listing_id": "uuid",
      "quantity": 50,
      "total_price": 20000.00,
      "status": "confirmed",
      "created_at": "2024-03-01T10:00:00",
      "listing_title": "Winter Jackets — Bulk Lot",
      "listing_city": "Lucknow",
      "seller_name": "Rahul Garments"
    }
  ]
}
```

---

### GET `/orders/seller/received`

Get all orders received on the seller's listings.

**Auth required:** Yes — `seller` only

**Success response `200`:**

```json
{
  "success": true,
  "message": "5 orders received",
  "data": [
    {
      "id": "uuid",
      "buyer_id": "uuid",
      "listing_id": "uuid",
      "quantity": 50,
      "total_price": 20000.00,
      "status": "pending",
      "created_at": "2024-03-01T10:00:00",
      "listing_title": "Winter Jackets — Bulk Lot",
      "listing_city": "Lucknow",
      "seller_name": "Rahul Garments"
    }
  ]
}
```

---

### PATCH `/orders/{order_id}/cancel`

Cancel a pending order. Restores stock back to the listing automatically.

**Auth required:** Yes — `buyer` only

**Success response `200`:**

```json
{
  "success": true,
  "message": "Order cancelled successfully",
  "data": { ...order object with status: "cancelled" }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `400` | Cannot cancel an order that is already {status} |
| `403` | You can only cancel your own orders |
| `404` | Order not found |

---

### PATCH `/orders/{order_id}/confirm`

Confirm a pending order. Seller acknowledges and accepts it.

**Auth required:** Yes — `seller` only

**Success response `200`:**

```json
{
  "success": true,
  "message": "Order confirmed",
  "data": { ...order object with status: "confirmed" }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `400` | Order is already {status} |
| `403` | You can only confirm orders on your own listings |
| `404` | Order not found |

---

### PATCH `/orders/{order_id}/complete`

Mark an order as completed. Only possible after confirmation.

**Auth required:** Yes — `seller` only

**Success response `200`:**

```json
{
  "success": true,
  "message": "Order marked as completed",
  "data": { ...order object with status: "completed" }
}
```

**Failure responses:**

| Status | Message |
|---|---|
| `400` | Order must be confirmed before marking complete |
| `403` | You can only complete orders on your own listings |
| `404` | Order not found |

---

## Analytics APIs

### GET `/analytics/trending`

Top 10 categories ranked by number of completed/confirmed orders across the platform.

**Auth required:** No

**Success response `200`:**

```json
{
  "success": true,
  "message": "Trending categories fetched",
  "data": [
    {
      "category": "Clothing",
      "total_orders": 42,
      "total_units_sold": 310,
      "total_revenue": 84500.00
    },
    {
      "category": "Electronics",
      "total_orders": 28,
      "total_units_sold": 95,
      "total_revenue": 142000.00
    }
  ]
}
```

---

### GET `/analytics/savings`

Platform-wide impact numbers. Shows total money saved vs original prices — the core environmental/financial impact metric.

**Auth required:** No

**Success response `200`:**

```json
{
  "success": true,
  "message": "Platform savings fetched",
  "data": {
    "total_saved_inr": 320000.00,
    "total_traded_value_inr": 180000.00,
    "original_value_inr": 500000.00,
    "avg_discount_pct": 64.0,
    "total_orders_completed": 87,
    "total_listings": 134,
    "active_listings": 61
  }
}
```

| Field | Description |
|---|---|
| `total_saved_inr` | Total ₹ saved vs original prices |
| `total_traded_value_inr` | Actual ₹ exchanged at discount prices |
| `original_value_inr` | What the same goods would have cost originally |
| `avg_discount_pct` | Average discount across all trades |
| `total_orders_completed` | Total fulfilled orders on platform |
| `total_listings` | All listings ever created |
| `active_listings` | Currently available listings |

---

### GET `/analytics/dashboard`

Personal seller dashboard — their listings, orders, and revenue breakdown.

**Auth required:** Yes — `seller` only

**Success response `200`:**

```json
{
  "success": true,
  "message": "Dashboard data fetched",
  "data": {
    "seller": {
      "id": "uuid",
      "business_name": "Rahul Garments",
      "city": "Lucknow"
    },
    "listings": {
      "active": 4,
      "sold": 2,
      "closed": 1,
      "total": 7
    },
    "orders": {
      "pending": 2,
      "confirmed": 3,
      "completed": 8,
      "cancelled": 1
    },
    "financials": {
      "total_revenue_inr": 45000.00,
      "total_units_sold": 180,
      "original_value_inr": 117000.00,
      "value_rescued_inr": 72000.00
    },
    "top_listing": {
      "title": "Winter Jackets Bulk",
      "revenue": 28000.00,
      "units": 112
    }
  }
}
```

| Field | Description |
|---|---|
| `listings` | Breakdown of all seller's listings by status |
| `orders` | Breakdown of all orders received by status |
| `total_revenue_inr` | Revenue from confirmed + completed orders only |
| `value_rescued_inr` | Difference between original value and sold value |
| `top_listing` | Best performing listing by revenue |

---

## Error Codes

| HTTP Status | Meaning |
|---|---|
| `400` | Bad request — validation failed or business rule violated |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — authenticated but wrong role or not the owner |
| `404` | Not found — resource does not exist |
| `422` | Unprocessable entity — request body has wrong types/missing fields |
| `500` | Internal server error |

---

## Order Status Flow

```
pending → confirmed → completed
pending → cancelled
```

- Only `buyer` can cancel — only while `pending`
- Only `seller` can confirm — moves `pending` → `confirmed`
- Only `seller` can complete — moves `confirmed` → `completed`
- Stock is restored automatically when an order is cancelled

---

## Listing Status Flow

```
active → sold       (auto when stock hits 0)
active → closed     (soft delete when orders exist)
active → deleted    (hard delete when no orders)
```