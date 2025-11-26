from fastapi import FastAPI
from contextlib import asynccontextmanager


from database.engine import init_db
from routes import (
    contacts_router,
    leads_router,
    operators_router,
    sources_router,
    stats_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Mini CRM", lifespan=lifespan)

for router in (
    contacts_router,
    leads_router,
    operators_router,
    sources_router,
    stats_router,
):
    app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
