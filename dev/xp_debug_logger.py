import os
import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "xp_debug.log")

def log_xp_update(current, max_xp):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}] XPBar.draw: Displayed XP = {current}/{max_xp}\n")

def log_update_ally_xp(current, max_xp):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}] update_ally_xp: True XP = {current}/{max_xp}\n")
