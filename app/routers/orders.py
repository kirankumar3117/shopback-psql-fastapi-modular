from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import postgreSql_pool
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/orders", tags=["Orders"])

class OrderSchema(BaseModel):
    product_id: int
    quantity: int

@router.post("/")
def create_order(order: OrderSchema):
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            #1 Checks stock (FOR UPDATES locks the row for safety)
            cursor.execute(
                "SELECT stock_quantity, price FROM products WHERE id = %s FOR UPDATE",
                (order.product_id,)
            )
            product = cursor.fetchone()

            #2 Now product['stock_qunatity'] works because of RealDictCursor!
            if not product or product['stock_quantity'] < order.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock")
            
            #3 Caluculate total and create the order
            total = product['price'] * order.quantity
            cursor.execute(
                "INSERT INTO orders (product_id, quantity, total_price) VALUES (%s, %s, %s)",
                (order.product_id, order.quantity, total)
            )

            #4 Decrease the stock
            cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s",
                (order.quantity, order.product_id)
            )

            #5 common part
            conn.commit()
            return {"message": "Order placed successfully", "total" : total}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        postgreSql_pool.putconn(conn)