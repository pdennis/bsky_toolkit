import sqlite3
from datetime import datetime
import os

class BlueskyDB:
    def __init__(self, db_path="bluesky_data.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS unfollowed_accounts (
                    did TEXT PRIMARY KEY,
                    handle TEXT,
                    unfollowed_at TIMESTAMP,
                    reason TEXT
                )
            """)
    
    def add_unfollowed_account(self, did, handle, reason="non_mutual"):
        """Record an unfollowed account."""
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT OR REPLACE INTO unfollowed_accounts (did, handle, unfollowed_at, reason)
                    VALUES (?, ?, ?, ?)
                """, (did, handle, datetime.utcnow().isoformat(), reason))
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def is_previously_unfollowed(self, did):
        """Check if an account was previously unfollowed."""
        try:
            cursor = self.conn.execute("""
                SELECT 1 FROM unfollowed_accounts WHERE did = ?
            """, (did,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_all_unfollowed(self):
        """Get all unfollowed accounts."""
        try:
            cursor = self.conn.execute("""
                SELECT * FROM unfollowed_accounts
                ORDER BY unfollowed_at DESC
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
