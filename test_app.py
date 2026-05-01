import httpx
import json

def test_pr_review():
    url = "http://127.0.0.1:8000/api/v1/review"
    
    # Mock data for a PR that has a security vulnerability
    payload = {
        "pr": 123,
        "repo": "salman1451/test-repo",
        "title": "Add database connection logic",
        "desc": "Setting up the initial DB connection helper.",
        "author": "dev-user",
        "raw_diff": """diff --git a/db.py b/db.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/db.py
@@ -0,0 +1,6 @@
+import os
+
+def get_connection():
+    # DANGER: Hardcoded password
+    conn_str = "mysql://admin:password123@localhost/db"
+    return conn_str
+"""
    }

    print("🚀 Sending Mock PR to Intelligence Engine...")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            print("\n✅ Review Completed!")
            print(f"Verdict: {result['decision'].upper()}")
            print(f"Severity: {result['severity'].upper()}")
            print(f"Style Score: {result['score']}/100")
            print("\n--- AI COMMENT ---")
            print(result['comment'])
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your server is running with: uvicorn app.main:app --reload")

if __name__ == "__main__":
    test_pr_review()
