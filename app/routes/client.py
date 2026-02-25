from fastapi import APIRouter

router = APIRouter()

@router.get('/client')
def client():
    return "This is client page"