from email import message
from os import access
from random import randrange
from re import S
from typing import List, Union
from colorama import AnsiToWin32

from pydantic import BaseModel

from fastapi import FastAPI, Response , status , Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

app = FastAPI()

class Settings(BaseModel):
    authjwt_secret_key : str = '44d98eb43c24f667c24e71ffa63a79bb75456e8947e84b7a0ba9afbad004a42d'


@AuthJWT.load_config
def get_config():
    return Settings()


class User(BaseModel):
  id: int
  fname:str
  lname:str
  email:str
  password:str

users = []
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/sign-up",status_code=status.HTTP_201_CREATED)
def create_user(user:User):
    user_dict = user.dict()
    user_dict['id'] = randrange(0,1000000)
    users.append(user_dict)
    return Response( content="user created succesfully" , status_code=status.HTTP_201_CREATED)


class UserLogin(BaseModel):
    email:str
    password:str


logined_users=[
    {
        "email":"asker@gmail.com",
        "password":"a1234"
    }
    ]

@app.get("/users",response_model=List[User])
def get_users():
    return users

@app.post("/user/{id}")
def get_user(id:int):
    for u in users:
        if u["id"]==id:
            return {"message":u}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    


@app.delete("/user/{id}")
def delete_user(id:int):
    for u in users:
        if u["id"]==id:
            users.remove(u)
            return {"message":f'user with id {id} deleted successfully'}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

@app.put("/user/{id}",status_code=status.HTTP_206_PARTIAL_CONTENT)
def update_user(user:User,id:int):
    for u in users:
        if u["id"]==id:
           u["fname"]=user.fname
           u["lname"]=user.lname
           u["password"]=user.password

           return {"message":f'user with id {id} updated successfully'}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
@app.post('/login')
def login(user:UserLogin,Authorize:AuthJWT=Depends()):
    for u in users:
        if (u["email"]==user.email) and (u["password"]==user.password):
            access_token =Authorize.create_access_token(subject=user.email)
            refresh_token=Authorize.create_refresh_token(subject=user.email)
            

            return {"acsess token":access_token , "refresh_token":refresh_token}
        raise HTTPException(status_code=401, detail="invalid user")  
          

@app.get("/protected")
def get_logged_in_user(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="invalid token")


    current_user=Authorize.get_jwt_subject()


    return {"current_user":current_user}

@app.get('/new_token')
def create_new_token(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="invalid token")
    current_user =Authorize.get_jwt_subject()
    access_token =Authorize.create_access_token(subject=current_user)

    return{"new_accsess_token":access_token}


@app.post('/fresh_login')
def fresh_login(user:UserLogin,Authorize:AuthJWT=Depends()):
    for u in users:
        if (u["email"]==user.email) and (u["password"]==user.password):
            fresh_token =Authorize.create_access_token(subject=user.email)
            return {"acsess_token":fresh_token}

        raise HTTPException(status_code=401, detail="invalid email or password")
            

@app.get('/fresh_url')
def get_user(Authorize:AuthJWT=Depends()):
    try:
        Authorize.fresh_jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid email or password")

    current_user =Authorize.get_jwt_subject()
    return{"current_user":current_user}


questions=[]
class Question(BaseModel):
    id:int
    question:str
    answers:List[str]



@app.get("/question")
def create_question(q:Question):
    questions.append(q.dict())
    return{"question":q}

@app.post("/question/{id}")
def read_question(id:int):
    for q in questions:
        if id == q["id"]:
            return{"question":q}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="question not found")


@app.post("/questions")
def read_all_questions(response_model=questions):
    if not questions:
        return {"message":"qustions is null"}
    return questions

@app.delete("/question/{id}")
def del_question(id:int):
    for q in questions:
        if id == q["id"]:
            questions.remove(q)
            return{"message":"question deleted"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="question not found")
