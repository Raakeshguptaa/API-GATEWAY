from fastapi import FastAPI , routing ,Request
from routes import client,admin





app = FastAPI()


app.include_router(client.router)
app.include_router(admin.route)




@app.get('/')
def homepage(request: Request):
    return {f"welcome to home page"}

