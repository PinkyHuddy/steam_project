import sqlite3
from pathlib import Path

db_path = Path("data/steam_ccu.db").resolve()
print("READING DB AT:", db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

rows = cur.execute("""
    SELECT timestamp, app_id, game_name, ccu
    FROM steam_ccu_log
    ORDER BY timestamp DESC
    LIMIT 5
""").fetchall()

print("Rows returned:", len(rows))
for r in rows:
    print(r)

conn.close()
