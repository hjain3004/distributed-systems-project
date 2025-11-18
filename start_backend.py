#!/usr/bin/env python
"""
Backend startup script
Ensures proper PYTHONPATH and module imports
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=3000,
        reload=False,  # Disable reload to avoid multiprocessing issues
        log_level="info"
    )
