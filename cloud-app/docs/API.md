# CloudApp API Documentation

API REST completa para CloudApp. Todos los endpoints requieren autenticación JWT excepto login y register.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

### Token-based (JWT)

Incluir en el header de todas las requests:

```
Authorization: Bearer {access_token}
```

### Refresh Token

```
POST /auth/refresh
Body:
{
  "refresh_token": "token"
}
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### Common Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `422`: Validation Error
- `500`: Internal Server Error

## Endpoints

### Authentication

#### Register User
```
POST /auth/register
Body:
{
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "password": "securepassword"
}
Response: User object
```

#### Login
```
POST /auth/login
Body:
{
  "email": "user@example.com",
  "password": "password"
}
Response:
{
  "access_token": "token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Logout
```
POST /auth/logout
Headers: Authorization: Bearer {token}
Response:
{
  "message": "Logged out successfully",
  "status": "success"
}
```

#### Change Password
```
POST /auth/change-password
Headers: Authorization: Bearer {token}
Body:
{
  "current_password": "current",
  "new_password": "new",
  "confirm_password": "new"
}
Response:
{
  "message": "Password changed successfully"
}
```

### Users

#### Get Current User Profile
```
GET /users/me
Headers: Authorization: Bearer {token}
Response: User object
```

#### Update Current User Profile
```
PUT /users/me
Headers: Authorization: Bearer {token}
Body:
{
  "email": "newemail@example.com",
  "full_name": "New Name",
  "phone": "+1234567890",
  "city": "New York",
  "country": "USA"
}
Response: User object
```

#### Get User by ID
```
GET /users/{user_id}
Headers: Authorization: Bearer {token}
Response: User object
```

#### List Users (Admin)
```
GET /users?skip=0&limit=10&is_active=true
Headers: Authorization: Bearer {token}
Query Parameters:
  - skip: number (default: 0)
  - limit: number (default: 10, max: 100)
  - is_active: boolean (optional)
Response:
{
  "items": [User objects],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

#### Activate User (Admin)
```
POST /users/{user_id}/activate
Headers: Authorization: Bearer {token}
Response:
{
  "message": "User activated"
}
```

#### Deactivate User (Admin)
```
POST /users/{user_id}/deactivate
Headers: Authorization: Bearer {token}
Response:
{
  "message": "User deactivated"
}
```

#### Delete User (Admin)
```
DELETE /users/{user_id}
Headers: Authorization: Bearer {token}
Response:
{
  "message": "User deleted successfully"
}
```

### Orders

#### Create Order
```
POST /orders
Headers: Authorization: Bearer {token}
Body:
{
  "user_id": 1,
  "description": "Order description",
  "notes": "Order notes",
  "items": [
    {
      "product_name": "Product 1",
      "sku": "SKU001",
      "quantity": 2,
      "price": 100.00,
      "discount": 10.00
    }
  ],
  "discount": 0,
  "tax": 20,
  "due_date": "2024-12-31T00:00:00"
}
Response: Order object
```

#### Get Order by ID
```
GET /orders/{order_id}
Headers: Authorization: Bearer {token}
Response: Order object
```

#### List Orders
```
GET /orders?skip=0&limit=10&status=pending
Headers: Authorization: Bearer {token}
Query Parameters:
  - skip: number (default: 0)
  - limit: number (default: 10)
  - status: pending|processing|completed|cancelled|on_hold (optional)
Response: Paginated list of orders
```

#### Update Order
```
PUT /orders/{order_id}
Headers: Authorization: Bearer {token}
Body:
{
  "status": "processing",
  "notes": "Updated notes",
  "items": [...],
  "discount": 50,
  "tax": 15
}
Response: Order object
```

#### Delete Order
```
DELETE /orders/{order_id}
Headers: Authorization: Bearer {token}
Response:
{
  "message": "Order deleted successfully"
}
```

#### Archive Order
```
POST /orders/{order_id}/archive
Headers: Authorization: Bearer {token}
Response:
{
  "message": "Order archived"
}
```

### Inventory

#### Create Inventory Item (Admin)
```
POST /inventory
Headers: Authorization: Bearer {token}
Body:
{
  "sku": "SKU001",
  "name": "Product Name",
  "category": "Category",
  "quantity": 100,
  "minimum_quantity": 10,
  "maximum_quantity": 500,
  "cost_price": 50.00,
  "selling_price": 100.00,
  "warehouse": "WH-1",
  "unit": "piece"
}
Response: Inventory object
```

#### Get Inventory Item
```
GET /inventory/{inventory_id}
Headers: Authorization: Bearer {token}
Response: Inventory object
```

#### List Inventory
```
GET /inventory?skip=0&limit=10&category=Electronics&low_stock=true
Headers: Authorization: Bearer {token}
Query Parameters:
  - skip: number
  - limit: number
  - category: string (optional)
  - warehouse: string (optional)
  - low_stock: boolean (optional)
Response: Paginated list
```

#### Update Inventory Item (Admin)
```
PUT /inventory/{inventory_id}
Headers: Authorization: Bearer {token}
Body:
{
  "name": "Updated Name",
  "quantity": 150,
  "selling_price": 120.00
}
Response: Inventory object
```

#### Delete Inventory Item (Admin)
```
DELETE /inventory/{inventory_id}
Headers: Authorization: Bearer {token}
```

#### Record Inventory Movement (Admin)
```
POST /inventory/{inventory_id}/movements
Headers: Authorization: Bearer {token}
Body:
{
  "movement_type": "in|out|adjustment|return",
  "quantity": 50,
  "reference": "ORD-001",
  "notes": "Stock in"
}
Response: Movement object
```

#### Search Inventory
```
GET /inventory/search?q=product
Headers: Authorization: Bearer {token}
Response: List of inventory items
```

#### Low Stock Items
```
GET /inventory/low-stock
Headers: Authorization: Bearer {token}
Response: List of low stock items
```

### Files

#### Upload File
```
POST /files/upload
Headers: Authorization: Bearer {token}
Content-Type: multipart/form-data
Body: file (binary)
Response:
{
  "filename": "file.pdf",
  "file_path": "user-1/file.pdf",
  "file_url": "https://...",
  "size": 12345,
  "content_type": "application/pdf"
}
```

#### Download File
```
GET /files/download/{file_path}
Headers: Authorization: Bearer {token}
Response: File binary
```

#### Delete File
```
DELETE /files/{file_path}
Headers: Authorization: Bearer {token}
Response:
{
  "message": "File deleted successfully"
}
```

#### Get File URL (Presigned)
```
GET /files/{file_path}/url?expires_in=3600
Headers: Authorization: Bearer {token}
Response:
{
  "url": "https://...",
  "expires_in": 3600
}
```

#### List User Files
```
GET /files
Headers: Authorization: Bearer {token}
Response:
{
  "files": [list of files],
  "total": 5
}
```

### Reports

#### Export Orders to Excel
```
GET /reports/orders/excel
Headers: Authorization: Bearer {token}
Response: Excel file
```

#### Export Orders to PDF
```
GET /reports/orders/pdf
Headers: Authorization: Bearer {token}
Response: PDF file
```

#### Export Inventory to Excel
```
GET /reports/inventory/excel
Headers: Authorization: Bearer {token}
Response: Excel file
```

#### Get Report Summary
```
GET /reports/summary
Headers: Authorization: Bearer {token}
Response:
{
  "total_orders": 100,
  "pending_orders": 10,
  "completed_orders": 85,
  "total_revenue": 50000,
  "total_users": 25,
  "total_inventory_items": 500,
  "low_stock_items": 15,
  "generated_at": "2024-01-15T10:30:00"
}
```

### Dashboard

#### Get Dashboard Statistics
```
GET /dashboard/stats
Headers: Authorization: Bearer {token}
Response:
{
  "orders": {...},
  "revenue": {...},
  "inventory": {...},
  "users": 50,
  "timestamp": "..."
}
```

#### Get Recent Orders
```
GET /dashboard/recent-orders?limit=10
Headers: Authorization: Bearer {token}
Response: List of recent orders
```

#### Get Inventory Status
```
GET /dashboard/inventory-status
Headers: Authorization: Bearer {token}
Response: Inventory statistics
```

#### Get Sales Chart Data
```
GET /dashboard/sales-chart?days=30
Headers: Authorization: Bearer {token}
Response:
{
  "period_days": 30,
  "data": [
    {
      "date": "2024-01-15",
      "orders": 5,
      "revenue": 1000.00
    }
  ]
}
```

## Rate Limiting

API endpoints are rate limited:

- General endpoints: 1000 requests per minute
- Auth endpoints: 100 requests per minute
- File upload: Depends on file size

Rate limit info is returned in headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1234567890
```

## Webhooks (Future)

Webhooks will be available for:
- Order created
- Order status changed
- Inventory level changed
- User registered

## Pagination

List endpoints support pagination:

```
GET /endpoint?skip=0&limit=10
```

Response format:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

## Filters

Most list endpoints support filtering:

```
GET /endpoint?status=active&category=electronics
```

See specific endpoint documentation for available filters.

## Versioning

Current API version: **v1**

Future versions will be available at `/api/v2`, etc.

## Support

For API issues:
1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Review [Swagger UI](http://localhost:8000/docs)
3. Open a GitHub issue
