from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor
from app.database import postgreSql_pool

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/category_sales")
def get_category_sales():
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # The "Triple join" with aggregation
            query = """
                SELECT
                    c.name AS category_name,
                    COUNT(o.id) AS total_orders,
                    COALESCE(SUM(o.total_price), 0) AS total_revenue
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                LEFT JOIN orders o ON p.id = o.product_id
                GROUP BY c.name
                ORDER BY total_revenue DESC NULLS LAST;
            """
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        print(f"Analytics Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        postgreSql_pool.putconn(conn)

@router.get("/top-products")
def get_top_products():
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # We join products and orders to see what's moving
            query="""
                SELECT
                    p.name
                    SUM(o.quantity) AS units_sold,
                    ROUND(SUM(o.total_price), 2) AS revenue
                FROM products p
                JOIN orders o ON p.id = o.product_id
                Group BY p.name
                ORDER BY units_sold DESC
                LIMIT 5
            """
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        print(f"Top products Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        postgreSql_pool.putconn(conn)