import sys
import os

sys.path.insert(0, r"C:\Users\franj\miniconda3\Lib\site-packages")

try:
    from notebooklm_mcp.server import get_client
    client = get_client()
    print("Client initialized successfully.")
    print("Testing call to list_notebooks...")
    notebooks = client.list_notebooks()
    print("Notebooks:", notebooks)
except Exception as e:
    import traceback
    traceback.print_exc()
