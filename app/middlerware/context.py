from contextvars import ContextVar


# DEPRICATED
# user_claims: ContextVar[dict | None] = ContextVar("user_claims", default=None)
request_id_var: ContextVar[str] = ContextVar("request_id", default="request_id")
