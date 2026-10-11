from pydantic import BaseModel, Field
from typing import Optional
from app.database import database_connection

#coffee or cafe business stuff

class MenuItemInput(BaseModel):
    """Validates data coming from the user when creating/updating an item."""
    name: str = Field(..., min_length=1, description="Name of the food or drink item")
    price: float = Field(..., ge=0.0, description="Price must be 0 or greater")

class MenuItem(MenuItemInput):
    """Represents a complete item directly out of our database."""
    id: int

    @classmethod
    def create(cls, name: str, price: float) -> int:
        """OOP Method: Adds a new menu item to the database."""
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO menu_items (name, price) VALUES (?, ?)",
                (name, price)
            )
            conn.commit()
            return cursor.lastrowid

    @classmethod
    def get_all(cls) -> list["MenuItem"]:
        """OOP Method: Fetches every item available on our menu."""
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price FROM menu_items")
            rows = cursor.fetchall()
            return [cls(id=row["id"], name=row["name"], price=row["price"]) for row in rows]



# order and transaction logics


class OrderInput(BaseModel):
    """Validates data when a customer places an order."""
    item_id: int = Field(..., description="The ID of the item being purchased")
    quantity: int = Field(..., ge=1, description="Must order at least 1 item")

class Order(OrderInput):
    """Represents a finished transaction record."""
    id: int
    total_price: float
    order_date: str

    @classmethod
    def place_order(cls, item_id: int, quantity: int) -> Optional["Order"]:
        """
        OOP Transaction Workflow: 
        1. Checks if item exists and gets price.
        2. Computes the transaction total automatically.
        3. Saves transaction record into the system database.
        """
        with database_connection() as conn:
            cursor = conn.cursor()
            
            # Step 1: Look up item to find its price
            cursor.execute("SELECT price FROM menu_items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
            if not item:
                return None  # Item doesn't exist!
                
            # Step 2: Automatically calculate total price
            calculated_total = item["price"] * quantity
            
            # Step 3: Insert order into database
            cursor.execute(
                """INSERT INTO orders (item_id, quantity, total_price) 
                   VALUES (?, ?, ?)""",
                (item_id, quantity, calculated_total)
            )
            conn.commit()
            order_id = cursor.lastrowid
            
            # Step 4: Fetch back completed record details
            cursor.execute("SELECT id, item_id, quantity, total_price, order_date FROM orders WHERE id = ?", (order_id,))
            saved_order = cursor.fetchone()
            
            return cls(
                id=saved_order["id"],
                item_id=saved_order["item_id"],
                quantity=saved_order["quantity"],
                total_price=saved_order["total_price"],
                order_date=str(saved_order["order_date"]))