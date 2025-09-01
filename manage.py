#!/usr/bin/env python3
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.brain_api.wsgi:app",
        host="0.0.0.0",
        port=12000,
        reload=False,
        proxy_headers=True,
        forwarded_allow_ips='*'
    )
