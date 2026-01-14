#!/usr/bin/env python3
"""Wrapper script for mcp dev command to start Inspector.

This script sets up the Python path and environment before importing the server.
It automatically starts the server in the background so Inspector can connect.

Usage: mcp dev test/test_mcp_inspector.py
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
# Since this file is in test/, we need to go up one level to get project root
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Load environment variables from .env if it exists
# This must happen BEFORE importing server, so that mcp instance is created with correct env vars
try:
    from netmind_web3_mcp.utils.env_loader import load_env_file
    env_file = project_root / ".env"
    if env_file.exists():
        load_env_file(project_root=project_root)
except Exception as e:
    # If loading fails, continue anyway (env vars might be set via export)
    pass

# Now import server - mcp instance will be created with the loaded environment variables
from netmind_web3_mcp import server

# Expose the mcp instance for mcp dev
# mcp dev will look for a variable named 'mcp' in this module
mcp = server.mcp

# Verify mcp instance is available
if mcp is None:
    raise RuntimeError("Failed to create MCP instance. Check server.py for errors.")

# When imported by mcp dev, we need to start the server in the background
# so that Inspector can connect to it via SSE
if __name__ != "__main__":
    # Running via mcp dev - start server in background thread
    import threading
    import time
    
    def start_server():
        """Start the server in a background thread using server.main().
        
        This delegates all initialization logic to server.main(), so we don't
        need to duplicate any code here. If server.py changes, this script
        automatically picks up those changes.
        """
        # Set transport to SSE for Inspector connection
        os.environ["MCP_TRANSPORT"] = "sse"
        
        # Simply call server.main() - it handles all initialization
        print("Starting MCP server in background for Inspector...")
        server.main()
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give server a moment to start
    time.sleep(2)
    print("MCP server should be running. Connect Inspector to: http://127.0.0.1:8000/sse")

# If running directly (not via mcp dev), start the server normally
if __name__ == "__main__":
    print("Starting MCP server...")
    print(f"MCP instance: {mcp}")
    print(f"Server name: {mcp.name if hasattr(mcp, 'name') else 'N/A'}")
    server.main()

