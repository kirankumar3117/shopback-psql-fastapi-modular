from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from app.database import postgreSql_pool

router = APIRouter(prefix="/products", tags=["Products"])

class ProductSchema(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int

class ProductUpdateSchema(BaseModel):
    category_id: int

@router.get("/")
def get_products(min_price: float = 0, limit: int = 5):
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # USING %s as placeholder to prevent SQL injection protection
            query = "SELECT * FROM products WHERE price >= %s LIMIT %s"
            cursor.execute(query, (min_price, limit))
            return cursor.fetchall()
    finally: 
        postgreSql_pool.putconn(conn)

@router.post("/")
def create_product(product: ProductSchema):
    # Borrow a connection from the pool
    conn = postgreSql_pool.getconn()
    try:
        # RealDictCursor makes results look like Python Dictionaries (JSON-like)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            INSERT INTO products (name, description, price, stock_quantity) 
            VALUES (%s, %s, %s, %s)
            RETURNING *;
            """
            cursor.execute(query, (product.name, product.description, product.price, product.stock_quantity))
            new_product = cursor.fetchone()
            conn.commit()
            return new_product
    except Exception as e:
        conn.rollback() #Undo the chnages if there's an error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always put the connection back in the pool
        postgreSql_pool.putconn(conn)

@router.put("/{product_id}")
def link_product_to_category(product_id: int, update_data: ProductUpdateSchema):
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # The SQL UPDATE command
            query = """
                UPDATE products
                SET category_id = %s
                WHERE id = %s
                RETURNING *;
            """
            cursor.execute(query, (update_data.category_id, product_id))
            updated_product = cursor.fetchone()

            if not updated_product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            conn.commit()
            return updated_product
    except Exception as e:
        conn.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        postgreSql_pool.putconn(conn)

@router.get("/detailed")
def get_detailed_products():
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT
                    p.id,
                    p.name AS product_name,
                    p.price,
                    c.name AS category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
            """
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail='Internal Server Error')
    finally:
        postgreSql_pool.putconn(conn)