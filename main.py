from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
from models import Base, Customer, Transaction, Loan

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class CustomerCreate(BaseModel):
    name: str
    balance: float = 0.0

class TransactionCreate(BaseModel):
    customer_id: int
    amount: float
    type: str

class LoanCreate(BaseModel):
    customer_id: int
    amount: float
    status: str

# Routes
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/customer")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = Customer(name=customer.name, balance=customer.balance)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return {"message": "Customer created!", "customer": customer}

@app.post("/transaction")
def create_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
    db_tx = Transaction(customer_id=tx.customer_id, amount=tx.amount, type=tx.type)
    db.add(db_tx)
    
    # Update balance
    customer = db.query(Customer).filter(Customer.id == tx.customer_id).first()
    if not customer:
        return {"error": "Customer not found"}
    customer.balance += tx.amount if tx.type == "credit" else -tx.amount
    
    db.commit()
    return {"message": "Transaction recorded!", "transaction": tx}

@app.post("/loan")
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    db_loan = Loan(customer_id=loan.customer_id, amount=loan.amount, status=loan.status)
    db.add(db_loan)
    db.commit()
    return {"message": "Loan request recorded!", "loan": loan}

@app.get("/customer/{customer_id}")
def get_customer_dashboard(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return {"error": "Customer not found"}
    
    transactions = db.query(Transaction).filter(Transaction.customer_id == customer_id).all()
    loans = db.query(Loan).filter(Loan.customer_id == customer_id).all()
    
    return {
        "customer": {"id": customer.id, "name": customer.name, "balance": customer.balance},
        "transactions": [{"amount": t.amount, "type": t.type, "date": t.date} for t in transactions],
        "loans": [{"amount": l.amount, "status": l.status} for l in loans]
    }
