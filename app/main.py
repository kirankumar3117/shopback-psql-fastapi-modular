from fastapi import FastAPI
from app.routers import products, categories, orders

app = FastAPI(title="Shop Backend Pro")

# Include the routers we just built
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(orders.router)


@app.get("/")
def root():
    return {"message": "Welcome to the Modular Shop API"}