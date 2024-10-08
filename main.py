import uvicorn
import os
import uuid
from uvicorn.config import Config
from fasthtml.common import *
from db import db


def user_auth_before(req, session):
    if "session_id" not in session:
        print("initializing session")
        session["session_id"] = str(uuid.uuid4())
        db.t.users.insert(
            id=session["session_id"],
            name="",
            email="",
            password="",
        )


beforeware = Beforeware(
    user_auth_before,
    skip=[r"/favicon\.ico", r"/static/.*", r".*\.css", r".*\.js", "/login"],
)

app, _ = fast_app(
    live=True,
    hdrs=(
        picolink,
        Link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
            type="text/css",
        ),
        MarkdownJS(),
        Script(
            src="https://unpkg.com/htmx-ext-response-targets@2.0.0/response-targets.js"
        ),
        Style(
            """
.main-page-loader{
    display:none;
}
.htmx-request.main-page-loader{
    display:inline;
    transform: translate(-50%, -50%);
    animation: pulse 2s ease-in-out infinite !important;
}
.btn-loader {
    position: relative;
    color: inherit;
    pointer-events: auto;
    opacity: 1;
}
.htmx-request.btn-loader {
    color: transparent;
    pointer-events: none;
}
.htmx-request.btn-loader::after {
    content: "Loading...";
    position: absolute;
    width: auto;
    height: auto;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #000000;
    font-size: 14px;
    animation: pulse 2s ease-in-out infinite !important;
}
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.2; }
    100% { opacity: 1; }
}
.error-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}
.error-modal .error-content {
    padding: 20px;
    border-radius: 5px;
    width: 80%;
    height: 80%;
    overflow: auto;
    position: relative;
    background-color: var(--pico-background-color);
    border: var(--pico-primary-border);
}
.error-modal .error-content .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 24px;
    cursor: pointer;
    border: none;
}pipp
    """
        ),
    ),
    exception_handlers={
        404: lambda req, exc: Main(
            Titled("Page not found"),
            P("The page you are looking for does not exist."),
            cls="container",
        ),
    },
    before=beforeware,
)

setup_toasts(app)


from app.views import home as home_views
from app.views import story as story_views
from app.controllers import plot as plot_controller
from app.controllers import init as init_controller

app.get("/")(home_views.home_view)

app.post("/init")(init_controller.initialize_story)

app.post("/story")(plot_controller.generate_plot)
app.get("/story")(story_views.story_view)

running_on_server = os.environ.get("RAILWAY_ENVIRONMENT_NAME") == "production"
serve(
    reload=not running_on_server,
    reload_excludes=["data/**"],
)
