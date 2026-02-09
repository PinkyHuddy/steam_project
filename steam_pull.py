import requests
from datetime import datetime, timezone
import time
import sqlite3
from pathlib import Path
import csv

URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"

APP_IDS = {
    "giants": {
        730: "CS2",
        570: "Dota 2",
        578080: "PUBG",
        1172470: "Apex Legends",
        271590: "GTA V",
    },
    "live_service": {
        1085660: "Destiny 2",
        252490: "Rust",
        230410: "Warframe",
        1599340: "Lost Ark",
    },
    "war_politics_adjacent": {
        1938090: "Call of Duty HQ",
        393380: "Squad",
        107410: "Arma 3",
        394360: "Hearts of Iron IV",
    },
    "control": {
        413150: "Stardew Valley",
        105600: "Terraria",
        1145360: "Hades",
        1086940: "Baldur's Gate 3",
    },
    "new_releases_hype": {
        1808500: "ARC Raiders",
        2767030: "Marvel Rivals",
    }
}

def get_current_players(app_id: int) -> int:
    response = requests.get(URL, params={"appid": app_id}, timeout=10)
    response.raise_for_status()

    data = response.json()
    steam_response = data.get("response", {})

    if steam_response.get("result") != 1:
        raise RuntimeError(f"Steam API returned error: {data}")

    return steam_response["player_count"]


CSV_PATH = Path("data/steam_ccu_log.csv")
CSV_PATH.parent.mkdir(exist_ok=True)

def append_to_csv(rows):
    file_exists = CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "category", "app_id", "game_name", "ccu"])
        for row in rows:
            writer.writerow(row)

DB_PATH = Path("data/steam_ccu.db")
DB_PATH.parent.mkdir(exist_ok=True)  # ensures data/ exists

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS steam_ccu_log (
    timestamp TEXT NOT NULL,
    app_id INTEGER NOT NULL,
    game_name TEXT NOT NULL,
    ccu INTEGER NOT NULL
)
""")
conn.commit()

if __name__ == "__main__":
    timestamp = datetime.now(timezone.utc).isoformat()
    rows = []

    for category, games in APP_IDS.items():
        for app_id, name in games.items():
            try:
                ccu = get_current_players(app_id)

                # SQLite (local)
                cur.execute(
                    "INSERT INTO steam_ccu_log (timestamp, app_id, game_name, ccu) VALUES (?, ?, ?, ?)",
                    (timestamp, app_id, name, ccu)
                )

                # CSV (cloud-friendly)
                rows.append([timestamp, category, app_id, name, ccu])

                print(f"Saved: {timestamp} | {category} | {name} ({app_id}) -> {ccu}")

            except Exception as e:
                print(f"Error for {name} ({app_id}): {e}")

            time.sleep(0.2)

    conn.commit()
    conn.close()

    append_to_csv(rows)