# open_mind_publishing/api.py
from ninja import NinjaAPI
from accounts.api import router as accounts_router  # <-- Import the app router

# The main entry point configuration
api = NinjaAPI(
    title="Open Mind Publishing API",
    version="1.0.0",
    description="Main Root API Gateway"
)

# Mount the accounts sub-router under the '/accounts' prefix
api.add_router("/accounts", accounts_router)
