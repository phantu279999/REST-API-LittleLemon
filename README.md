# API LittleLemon Restaurants

#### User Group(Manager, Delivery crew)


### List Endpoint

#### /auth/users
    Creates a new user with name, email and password
#### /auth/users/me
    Displays only the current user
#### /auth/token/login
    Generates access tokens that can be used in other API calls in this project
#### /api/menu-items
    Lists all menu items. 
#### /api/menu-items/{id}
    Lists single menu item
#### /api/groups/{group_name}/users/
    Returns all users in group
#### /api/cart/menu-items
    Returns current items in the cart for the current user token
#### /api/orders
    Returns all orders with order items created by this user
#### /api/orders/{orderId}
    Returns all items for this order id. If the order ID doesn’t belong to the current user, it displays an appropriate HTTP error status code.
