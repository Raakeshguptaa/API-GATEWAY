from fastapi import APIRouter

router = APIRouter()


@router.get('/admin')
def admin():
    return "this is admin page"