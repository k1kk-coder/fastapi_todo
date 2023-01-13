from fastapi import APIRouter


company_router = APIRouter()


@company_router.get("/")
async def get_company_name():
    return {"Company name": "Example company"}


@company_router.get("/employees")
async def get_number_of_employees():
    return 179
