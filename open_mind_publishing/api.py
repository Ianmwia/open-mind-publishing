# open_mind_publishing/api.py
from ninja import NinjaAPI
from accounts.api import router as accounts_router
from projects.api import router as projects_router
from allauth.headless.contrib.ninja.security import jwt_token_auth

# The main entry point configuration
api = NinjaAPI(
    title="Open Mind Publishing Management API",
    version="1.0.0",
    description="Publishing Management System for Digital, Language, and Chart projects"
)

# Mount sub-routers
api.add_router("/accounts", accounts_router, auth=jwt_token_auth)
api.add_router("/projects", projects_router, auth=jwt_token_auth)
