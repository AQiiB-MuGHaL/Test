import time
import requests

# --- Config ---
BOT_TOKEN = "8931091996:AAHgcTH38hSH1RXFVzEcqNR2O1LKtqS3RBk"
CHAT_ID = "7883547875"

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': text}
        requests.post(url, data=payload, timeout=10)
    except Exception:
        pass

if __name__ == "__main__":
    # Startup test message
    send_msg("🚀 Main Script Started: Request Successful! Bot is online.")
    
    while True:
        try:
            # Har 10 minutes baad test message bhejy ga (600 seconds)
            send_msg("✅ Request Successful! Background daemon is running.")
        except Exception:
            pass
            
        # 10 Minutes Interval
        time.sleep(600)
