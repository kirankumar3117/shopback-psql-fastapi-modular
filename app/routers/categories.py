from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from app.database import postgreSql_pool

router = APIRouter(prefix="/categories", tags=["Categories"])

class CategorySchema(BaseModel):
    name: str


@router.post("/")
def create_category(category: CategorySchema):
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                'INSERT INTO categories (name) VALUES (%s) RETURNING *;',
                (category.name,)
            )
            new_cat = cursor.fetchone()
            conn.commit()
            return new_cat
    except Exception as e:
        conn.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        postgreSql_pool.putconn(conn)

@router.get("/")
def get_categories():
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Simple query to get everything from the categories table
            cursor.execute(
                "SELECT * FROM categories ORDER BY name ASC"
            )
            return cursor.fetchall()
    except Exception as e:
        conn.rollback()
        print(f"Database Error: {e}")
    finally:
        postgreSql_pool.putconn(conn)

@router.delete("/{category_id}")
def delete_category(category_id: str):
    conn = postgreSql_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            #Delete the category
            cursor.execute("DELETE FROM categories WHERE id = %s RETURNING *;", (category_id))
            delete_cat = cursor.fetchone()

            if not delete_cat:
                raise HTTPException(status_code=400, detail="Category not found")
            
            conn.commit()
            return {"message": f"Category '{delete_cat['name']}' deleted successfully"}
    except Exception as e:
         conn.rollback()
         print(f"Databas Error: {e}")
         raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        postgreSql_pool.putconn(conn)