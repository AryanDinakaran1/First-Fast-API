import hashlib

from mysql import connector
from decouple import config

from fastapi import FastAPI, Request, Form
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

db = connector.connect(
        host = config('DB_HOST'),
        user = config('DB_USER'),
        password = config('DB_PASSWORD'),
        database = config('DB_NAME')
    )

my_cursor = db.cursor()

@app.get('/home/{user}')
def index(request: Request, user: str):

    if not user:
        return RedirectResponse('/signinview')

    my_cursor.execute(f"SELECT is_login FROM users WHERE name = '{user}'")
    myresult = my_cursor.fetchall()[0][0]

    if myresult == 'False':
        return RedirectResponse('/signinview')

    return templates.TemplateResponse('index.html', {
        'request' : request,
        'user' : user
    })

@app.get('/logout/{user}')
def logout(user: str):
    sql = f"UPDATE users SET is_login = 'False' WHERE name = '{user}'"
    my_cursor.execute(sql)
    db.commit()

    return RedirectResponse(f'/signinview', status_code=303)

@app.get('/signinview')
def signinview(request: Request):

    return templates.TemplateResponse('signin.html', {
        'request' : request
    })

@app.get('/signupview')
def signupview(request: Request):
    return templates.TemplateResponse('signup.html', {
        'request' : request
    })

@app.post('/signup')
def signup(username: str = Form(...), password: str = Form(...)):
    insert = "INSERT INTO users (name, password, is_login) VALUES (%s,%s,%s)"
    val = (username, hashlib.sha256(password.encode()).hexdigest(), 'True')
    my_cursor.execute(insert, val)

    db.commit()

    return RedirectResponse(f'/home/{username}', status_code=303)

@app.post('/signin')
def signin(username: str = Form(...), password: str = Form(...)):
    my_cursor.execute(f"SELECT password FROM users WHERE name = '{username}'")
    myresult = my_cursor.fetchall()[0][0]

    hashedPassword = hashlib.sha256(password.encode()).hexdigest()

    if hashedPassword == myresult:
        sql = f"UPDATE users SET is_login = 'True' WHERE name = '{username}'"
        my_cursor.execute(sql)
        db.commit()
        
        return RedirectResponse(f'/home/{username}', status_code=303)
    else:
        return RedirectResponse(f'/signinview', status_code=303)