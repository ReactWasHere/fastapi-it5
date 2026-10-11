from fastapi import FastAPI, HTTPException, status
from app.database import database_connection
from app.models import MenuItemInput, MenuItem, OrderInput, Order

app = FastAPI(
    title="BEEN DRINKING CAFE! Information & Ordering System",
    description="A simple information system managing menu records and transactional customer orders.",
    version="1.0.0"
)

@app.get("/", tags=["General"])
def root():
    """Welcome root path endpoint."""
    return {"message": "Welcome to the BEEN DRINKING CAFE! Management System API!"}



# menu management the crud management


@app.post("/menu/", response_model=MenuItem, status_code=status.HTTP_201_CREATED, tags=["Menu CRUD"])
def add_menu_item(item: MenuItemInput):
    """CREATE: Adds a brand new item to the cafe menu."""
    try:
        new_id = MenuItem.create(name=item.name, price=item.price)
        return MenuItem(id=new_id, name=item.name, price=item.price)
    except Exception:
        raise HTTPException(status_code=400, detail="An item with this name already exists.")

@app.get("/menu/", response_model=list[MenuItem], tags=["Menu CRUD"])
def get_menu():
    """READ: Retrieves all available items on the current menu."""
    return MenuItem.get_all()

@app.put("/menu/{item_id}", response_model=MenuItem, tags=["Menu CRUD"])
def update_menu_item(item_id: int, updated_item: MenuItemInput):
    """UPDATE: Modifies the details (name or price) of an existing menu item."""
    with database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE menu_items SET name = ?, price = ? WHERE id = ?",
            (updated_item.name, updated_item.price, item_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Menu item with ID {item_id} not found.")
        
    return MenuItem(id=item_id, name=updated_item.name, price=updated_item.price)

@app.delete("/menu/{item_id}", tags=["Menu CRUD"])
def delete_menu_item(item_id: int):
    """DELETE: Permanently removes an item from the menu."""
    with database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Menu item with ID {item_id} not found.")
            
    return {"message": f"Menu item with ID {item_id} was successfully deleted."}


 
# Transactional order processing and logging

@app.post("/orders/", response_model=Order, status_code=status.HTTP_201_CREATED, tags=["Transactions"])
def place_new_order(order: OrderInput):
    """
    TRANSACTION: Processes an incoming customer food/beverage order.
    It lookups the product price, calculates totals, and saves the transaction logs.
    """
    completed_order = Order.place_order(item_id=order.item_id, quantity=order.quantity)
    if not completed_order:
        raise HTTPException(
            status_code=404, 
            detail=f"Cannot complete order. Menu item ID {order.item_id} does not exist."
        )
    return completed_order