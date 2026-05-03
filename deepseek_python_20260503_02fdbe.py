import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('dumping_bot.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dumped_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_chat_id INTEGER,
                message_id INTEGER,
                target_chat_id INTEGER,
                timestamp TEXT,
                UNIQUE(source_chat_id, message_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dumping_status (
                source_chat_id INTEGER PRIMARY KEY,
                is_active INTEGER DEFAULT 1,
                last_message_id INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT,
                source_chat_id INTEGER,
                count INTEGER,
                PRIMARY KEY(date, source_chat_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_dumped_message(self, source_id, msg_id, target_id):
        try:
            self.cursor.execute(
                "INSERT INTO dumped_messages (source_chat_id, message_id, target_chat_id, timestamp) VALUES (?, ?, ?, ?)",
                (source_id, msg_id, target_id, datetime.now().isoformat())
            )
            self.conn.commit()
            return True
        except:
            return False
    
    def is_already_dumped(self, source_id, msg_id):
        self.cursor.execute(
            "SELECT 1 FROM dumped_messages WHERE source_chat_id = ? AND message_id = ?",
            (source_id, msg_id)
        )
        return self.cursor.fetchone() is not None
    
    def get_dumping_status(self, source_id):
        self.cursor.execute("SELECT is_active, last_message_id FROM dumping_status WHERE source_chat_id = ?", (source_id,))
        row = self.cursor.fetchone()
        return (True, 0) if not row else (bool(row[0]), row[1] or 0)
    
    def set_dumping_status(self, source_id, is_active):
        self.cursor.execute(
            "INSERT OR REPLACE INTO dumping_status (source_chat_id, is_active) VALUES (?, ?)",
            (source_id, 1 if is_active else 0)
        )
        self.conn.commit()
    
    def update_last_message_id(self, source_id, msg_id):
        self.cursor.execute(
            "INSERT OR REPLACE INTO dumping_status (source_chat_id, is_active, last_message_id) VALUES (?, COALESCE((SELECT is_active FROM dumping_status WHERE source_chat_id = ?), 1), ?)",
            (source_id, source_id, msg_id)
        )
        self.conn.commit()
    
    def increment_stat(self, source_id):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            "INSERT INTO daily_stats (date, source_chat_id, count) VALUES (?, ?, 1) ON CONFLICT(date, source_chat_id) DO UPDATE SET count = count + 1",
            (today, source_id)
        )
        self.conn.commit()
    
    def get_daily_stats(self, source_id=None):
        today = datetime.now().strftime("%Y-%m-%d")
        if source_id:
            self.cursor.execute("SELECT count FROM daily_stats WHERE date = ? AND source_chat_id = ?", (today, source_id))
            row = self.cursor.fetchone()
            return row[0] if row else 0
        else:
            self.cursor.execute("SELECT SUM(count) FROM daily_stats WHERE date = ?", (today,))
            return self.cursor.fetchone()[0] or 0
    
    def get_monthly_stats(self, source_id=None):
        month = datetime.now().strftime("%Y-%m")
        if source_id:
            self.cursor.execute("SELECT SUM(count) FROM daily_stats WHERE date LIKE ? AND source_chat_id = ?", (f"{month}%", source_id))
            return self.cursor.fetchone()[0] or 0
        else:
            self.cursor.execute("SELECT SUM(count) FROM daily_stats WHERE date LIKE ?", (f"{month}%",))
            return self.cursor.fetchone()[0] or 0
    
    def get_source_stats(self, source_id):
        self.cursor.execute("SELECT COUNT(*) FROM dumped_messages WHERE source_chat_id = ?", (source_id,))
        total = self.cursor.fetchone()[0]
        daily = self.get_daily_stats(source_id)
        monthly = self.get_monthly_stats(source_id)
        return {"total": total, "daily": daily, "monthly": monthly}
    
    def close(self):
        self.conn.close()