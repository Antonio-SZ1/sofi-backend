from fastapi import FastAPI
from app.api.routers import clients, loans, auth

app = FastAPI(
    title="SOFIPO Backend API",
    description="Backend para un mini sistema de Sociedad Financiera Popular.",
    version="1.0.0"
)

api_prefix = "/api/v1"
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
app.include_router(clients.router, prefix=f"{api_prefix}/clients", tags=["Clients"])
app.include_router(loans.router, prefix=f"{api_prefix}/loans", tags=["Loans & Payments"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a SOFIPO API"}