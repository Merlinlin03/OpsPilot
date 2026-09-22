import uvicorn

from app.config.config import settings

if __name__ == "__main__":
    uvicorn.run("app.api.app:app",
                host=settings.app_host,
                port=settings.app_port,
                reload=False)
