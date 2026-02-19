import aiosqlite
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Strip the SQLAlchemy prefix for raw aiosqlite usage
DB_PATH = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")


async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS players (
                oauth_id          TEXT PRIMARY KEY,
                username          TEXT NOT NULL,
                provider          TEXT NOT NULL,
                email             TEXT,
                legacy_spellbook  TEXT DEFAULT '[]',
                grimoire_count    INTEGER DEFAULT 0,
                is_banned         INTEGER DEFAULT 0,
                last_login        TIMESTAMP,
                created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Migrate existing DBs: add new columns if they don't exist yet
            -- (SQLite does not support IF NOT EXISTS on ALTER TABLE columns,
            --  so we catch the error in Python instead — see init_db below)

            CREATE TABLE IF NOT EXISTS runs (
                id          TEXT PRIMARY KEY,
                player_id   TEXT NOT NULL,
                class       TEXT NOT NULL,
                state_json  TEXT NOT NULL DEFAULT '{}',
                floor       INTEGER DEFAULT 1,
                status      TEXT DEFAULT 'active',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(oauth_id)
            );

            CREATE TABLE IF NOT EXISTS grimoire (
                ingredient_key   TEXT NOT NULL,
                variant_index    INTEGER NOT NULL DEFAULT 0,
                spell_name       TEXT NOT NULL,
                flavor_text      TEXT,
                stats_json       TEXT NOT NULL DEFAULT '{}',
                effects_json     TEXT NOT NULL DEFAULT '[]',
                ingredient_tiers TEXT NOT NULL DEFAULT '{}',
                luck_threshold   INTEGER DEFAULT 0,
                discovered_by    TEXT,
                discovered_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ingredient_key, variant_index)
            );

            CREATE INDEX IF NOT EXISTS idx_runs_player ON runs(player_id);
            CREATE INDEX IF NOT EXISTS idx_grimoire_key ON grimoire(ingredient_key);
        """)
        await db.commit()

        # ── Migrate existing databases ────────────────────────────────────────
        # SQLite doesn't support "ALTER TABLE ... ADD COLUMN IF NOT EXISTS",
        # so we attempt each migration and silently skip if already applied.
        migrations = [
            "ALTER TABLE players ADD COLUMN email TEXT",
            "ALTER TABLE players ADD COLUMN is_banned INTEGER DEFAULT 0",
            "ALTER TABLE players ADD COLUMN last_login TIMESTAMP",
            # Password-based auth additions
            "ALTER TABLE players ADD COLUMN password_hash TEXT",
            "ALTER TABLE players ADD COLUMN auth_method TEXT NOT NULL DEFAULT 'oauth'",
            # OAuth ↔ password merge: records which OAuth provider was linked to a
            # password account without overwriting the canonical `provider` field.
            "ALTER TABLE players ADD COLUMN linked_provider TEXT",
        ]
        for sql in migrations:
            try:
                await db.execute(sql)
                await db.commit()
            except aiosqlite.OperationalError:
                pass  # Column already exists — safe to ignore

