from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Hello World", description="这是一个测试接口")
async def read_root():
    a = 1
    b = 2
    c = a + b
    print(c)
    return {"Hello": "World"}
