import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.routes.auth import login_router
from api.routes.user import user_router


""" API ROUTERS """

app = FastAPI(title="plygramm-uni")

# create instanse for the routers
main_api_router = APIRouter()

# set routers to the app instance
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(login_router, prefix="/login", tags=["login"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
