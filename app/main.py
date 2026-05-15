from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from jinja2 import Environment, FileSystemLoader
import os

from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="A secure Todo Application with MySQL backend",
    version="1.0.0",
    docs_url=None if not settings.DEBUG else "/docs",
    redoc_url=None if not settings.DEBUG else "/redoc",
    openapi_url=None if not settings.DEBUG else "/openapi.json",
)

trusted_hosts = ["localhost", "127.0.0.1", "8.136.51.220"]
if settings.DEBUG:
    trusted_hosts.append("*")

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=trusted_hosts,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=True,
)


def render_template(template_name: str, **context) -> str:
    try:
        template = jinja_env.get_template(template_name)
        return template.render(**context)
    except Exception:
        return f"<h1>404</h1><p>Template {template_name} not found</p>"



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api/"):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    error_page = os.path.join(TEMPLATES_DIR, "error.html")
    if os.path.exists(error_page):
        with open(error_page, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content.replace("{{error_message}}", str(exc.detail)), status_code=exc.status_code)
    return HTMLResponse(content=f"<h1>{exc.status_code} Error</h1><p>{exc.detail}</p>", status_code=exc.status_code)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


from app.api.auth import router as auth_router
from app.api.todos import router as todos_router
from app.api.tags import router as tags_router
from app.api.statistics import router as statistics_router
from app.api.export import router as export_router
from app.api.collaboration import router as collaboration_router
from app.api.calendar_api import router as calendar_router
from app.api.reminders import router as reminders_router

app.include_router(auth_router)
app.include_router(todos_router)
app.include_router(tags_router)
app.include_router(statistics_router)
app.include_router(export_router)
app.include_router(collaboration_router)
app.include_router(calendar_router)
app.include_router(reminders_router)


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=render_template("index.html"))


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(content=render_template("auth/login.html"))


@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return HTMLResponse(content=render_template("auth/register.html"))


@app.get("/todos", response_class=HTMLResponse)
async def todos_page():
    return HTMLResponse(content=render_template("todos/list.html"))


@app.get("/calendar", response_class=HTMLResponse)
async def calendar_page():
    return HTMLResponse(content=render_template("calendar.html"))


@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page():
    return HTMLResponse(content=render_template("statistics.html"))


@app.get("/pomodoro", response_class=HTMLResponse)
async def pomodoro_page():
    return HTMLResponse(content=render_template("pomodoro.html"))


@app.get("/collaboration", response_class=HTMLResponse)
async def collaboration_page():
    return HTMLResponse(content=render_template("collaboration.html"))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}


if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
async def startup_event():
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
