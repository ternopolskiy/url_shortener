"""
Database Migrations Module
Auto-run migrations on application startup
"""

import sqlite3
from pathlib import Path
from app.config import settings


def get_db_path() -> Path:
    """Get database path from settings."""
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        return Path(db_url.replace("sqlite:///./", ""))
    return Path("gosha.db")


def run_language_migration(conn: sqlite3.Connection) -> None:
    """Run migration for language column in users table."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'language' not in columns:
        print("🔄 Running migration: Adding 'language' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN language VARCHAR(5) DEFAULT 'en'")
        conn.commit()
        print("✅ Migration completed: 'language' column added")


def run_qr_migration(conn: sqlite3.Connection) -> None:
    """Run migration for QR codes table."""
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='qr_codes'")
    
    if not cursor.fetchone():
        # Table doesn't exist - create it
        print("🔄 Creating qr_codes table...")
        _create_qr_table(cursor)
        conn.commit()
        print("✅ QR codes table created successfully")
        return
    
    # Check if migration needed
    cursor.execute("PRAGMA table_info(qr_codes)")
    qr_columns = [col[1] for col in cursor.fetchall()]
    required_columns = ['content', 'title', 'qr_image_base64', 'box_size', 
                       'border_size', 'logo_base64', 'error_correction', 
                       'downloads_count', 'updated_at']
    missing = [c for c in required_columns if c not in qr_columns]
    
    if not missing:
        print("✅ QR codes table is up to date")
        return
    
    # Migrate existing table
    print(f"🔄 Migrating qr_codes table (missing: {', '.join(missing)})...")
    _migrate_qr_table(cursor)
    conn.commit()
    print("✅ QR codes table migrated successfully")


def _create_qr_table(cursor: sqlite3.Cursor) -> None:
    """Create qr_codes table with full schema."""
    cursor.execute("""
        CREATE TABLE qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            url_id INTEGER,
            content VARCHAR(2000) NOT NULL,
            title VARCHAR(200),
            qr_image_base64 TEXT NOT NULL,
            foreground_color VARCHAR(7) DEFAULT '#000000',
            background_color VARCHAR(7) DEFAULT '#FFFFFF',
            style VARCHAR(20) DEFAULT 'square',
            box_size INTEGER DEFAULT 10,
            border_size INTEGER DEFAULT 4,
            logo_base64 TEXT,
            error_correction VARCHAR(1) DEFAULT 'M',
            downloads_count INTEGER DEFAULT 0,
            created_at DATETIME,
            updated_at DATETIME,
            qr_data VARCHAR(2000),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (url_id) REFERENCES urls(id)
        )
    """)
    cursor.execute("CREATE INDEX idx_qr_codes_user_id ON qr_codes(user_id)")
    cursor.execute("CREATE INDEX idx_qr_codes_url_id ON qr_codes(url_id)")


def _migrate_qr_table(cursor: sqlite3.Cursor) -> None:
    """Migrate existing qr_codes table to new schema."""
    # Backup data
    cursor.execute("SELECT * FROM qr_codes")
    rows = cursor.fetchall()
    old_columns = [col[1] for col in cursor.description]
    data_backup = [dict(zip(old_columns, row)) for row in rows]
    
    # Drop and recreate
    cursor.execute("DROP TABLE qr_codes")
    _create_qr_table(cursor)
    
    # Restore data
    for data in data_backup:
        content = data.get('content') or data.get('qr_data') or 'https://example.com'
        cursor.execute("""
            INSERT INTO qr_codes (
                id, user_id, url_id, content, title, qr_image_base64,
                foreground_color, background_color, style,
                box_size, border_size, logo_base64, error_correction,
                downloads_count, created_at, updated_at, qr_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('id'), data.get('user_id'), data.get('url_id'),
            content, data.get('title'),
            data.get('qr_image_base64') or data.get('qr_data', ''),
            data.get('foreground_color', '#000000'),
            data.get('background_color', '#FFFFFF'),
            data.get('style', 'square'),
            data.get('box_size', 10),
            data.get('border_size', 4),
            data.get('logo_base64'),
            data.get('error_correction', 'M'),
            data.get('downloads_count', 0),
            data.get('created_at'), data.get('updated_at'),
            data.get('qr_data')
        ))


def run_all_migrations() -> None:
    """Run all database migrations on startup."""
    db_path = get_db_path()
    print(f"🔍 Checking database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    try:
        print("🔄 Running database migrations...")
        run_language_migration(conn)
        run_qr_migration(conn)
        print("✅ All migrations completed")
    except Exception as e:
        print(f"⚠️  Migration error: {e}")
        raise
    finally:
        conn.close()
