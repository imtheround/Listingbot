import subprocess
import json
import os
import getUuid
from getUuid import get_uuid
import asyncio
def run_js_fetchstat(username, uuid) -> dict:
    js_file_path = os.path.join("utils", "fetchstat.js")
    try:
        result = subprocess.run(
            ["node", "fetchNetworth.js", uuid, username],
            capture_output=True,
            text=True,
            check=True
        )
        output = json.loads(result.stdout)
        return output
    except subprocess.CalledProcessError as e:
        print("JavaScript execution failed:", e.stderr)
        return {"sucess": False, "cause": "JavaScript execution failed"}
    except json.JSONDecodeError:
        print("Failed to parse JSON output from JavaScript.")
        return {"sucess": False, "cause": "Failed to parse JSON output from JavaScript."}

