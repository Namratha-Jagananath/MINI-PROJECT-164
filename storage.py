"""
Storage Module (M6)

SQLite-based storage for discovered onion services.
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class ServiceRecord:
    url: str
    first_seen_at: str
    last_checked_at: Optional[str] = None
    is_active: Optional[bool] = None
    content_hash: Optional[str] = None
    is_mirror_of: Optional[str] = None
    source: Optional[str] = None


class DataStore:
    """Stores discovered services using SQLite."""

    def __init__(self, database_path: str = "tor_services.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)

        self.create_table()

    def create_table(self):
        """Create the services table if it does not exist."""

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_checked_at TEXT,
                is_active INTEGER,
                content_hash TEXT,
                is_mirror_of TEXT,
                source TEXT
            )
            """
        )

        self.connection.commit()

    def add_service(self, record: ServiceRecord):
        """Add a service if it does not already exist."""

        self.connection.execute(
            """
            INSERT OR IGNORE INTO services (
                url,
                first_seen_at,
                last_checked_at,
                is_active,
                content_hash,
                is_mirror_of,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.url,
                record.first_seen_at,
                record.last_checked_at,
                record.is_active,
                record.content_hash,
                record.is_mirror_of,
                record.source,
            ),
        )

        self.connection.commit()

    def get_all_services(self):
        """Return all stored services."""

        cursor = self.connection.execute(
            """
            SELECT
                url,
                first_seen_at,
                last_checked_at,
                is_active,
                content_hash,
                is_mirror_of,
                source
            FROM services
            ORDER BY id
            """
        )

        return cursor.fetchall()

    def count_services(self):
        """Return the number of stored services."""

        cursor = self.connection.execute(
            "SELECT COUNT(*) FROM services"
        )

        return cursor.fetchone()[0]

    def close(self):
        """Close the database connection."""

        self.connection.close()


if __name__ == "__main__":

    store = DataStore()

    print("========================================")
    print("          TOR SERVICE STORAGE")
    print("========================================")

    print("Database: tor_services.db")
    print("Stored services:", store.count_services())

    store.close()
