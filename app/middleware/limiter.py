from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.exceptions import RateLimitException


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        minute_ago = now - 60
        
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        if len(self.requests[client_ip]) >= self.settings.RATE_LIMIT_PER_MINUTE:
            raise RateLimitException()
        
        self.requests[client_ip].append(now)
        return await call_next(request)