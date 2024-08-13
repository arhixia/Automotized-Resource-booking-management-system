from fastapi import FastAPI
from src.users import router as users_router
from src.booking import booking_router as booking_router
from src.schedule import schedule_router as schedule_router
from src.resource import resource_router as resource_router
app = FastAPI()


app.include_router(users_router)
app.include_router(booking_router)
app.include_router(schedule_router)
app.include_router(resource_router)








