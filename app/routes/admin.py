from fastapi import APIRouter

route = APIRouter()

@route.get('/admin')
def admin():
    return "this is admin page"