import uvicorn

from common import application, settings

app = application.init_app()

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=settings.settings.SERVER_HOST,
        port=settings.settings.SERVER_PORT,
        reload=settings.settings.RELOAD,
        use_colors=settings.settings.DEBUG,
    )
