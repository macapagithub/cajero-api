from db.user_db import UserInDB
from db.user_db import update_user, get_user

from db.transaction_db import TransactionInDB
from db.transaction_db import save_transaction

from models.user_models import UserIn, UserOut
from models.transaction_models import TransactionIn, TransactionOut


import datetime 
from fastapi import FastAPI 
from fastapi import HTTPException
api = FastAPI()


from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost.tiangolo.com","https://localhost.tiangolo.com",
    "http://localhost","http://localhost:8080",
]

api.add_middleware(
    CORSMiddleware, allow_origins = origins,
    allow_credentials = True, allow_methods = ["*"], allow_headers = ["*"],
)

@api.get("/")
async def home():
    return {"message": "Bienvenido a su cajero"}

@api.post("/user/auth/")
async def auth_user(user_in: UserIn):
    user_in_db = get_user(user_in.username)
    if user_in_db == None:
        raise HTTPException(status_code = 404, detail = "El usuario no existe")
    if user_in_db.password != user_in.password:
        return{"Autenticado": False}
    return{"Autenticado":True}


@api.get("/user/balance/{username}")
async def get_balance(username: str):
    user_in_db = get_user(username)
    if user_in_db == None:
        raise HTTPException(status_code = 404, detail = "El usuario no existe")
    user_out = UserOut(**user_in_db.dict())
    return user_out

@api.put("/user/transaction/")
async def make_transaction(transaction_in: TransactionIn):
    user_in_db = get_user(transaction_in.username)
    if user_in_db == None:
        raise HTTPException(status_code = 404, detail = "El usuario no existe")
    if user_in_db.balance < transaction_in.value:
        raise HTTPException(status_code = 400,detail = "Sin fondos suficientes")

    user_in_db.balance = user_in_db.balance - transaction_in.value
    update_user(user_in_db)

    transaction_in_db = TransactionInDB(**transaction_in.dict(), actual_balance = user_in_db.balance)
    transaction_in_db = save_transaction(transaction_in_db)

    transaction_out = TransactionOut(**transaction_in_db.dict())
    return transaction_out
