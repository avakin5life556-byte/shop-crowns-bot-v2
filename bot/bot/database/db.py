import sqlite3
import threading
from datetime import datetime
from typing import Optional, Dict, List, Any
import pytz

TIMEZONE = pytz.timezone('Africa/Cairo')


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connection and create all tables"""
        self.conn = sqlite3.connect('shop_crowns.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._create_indexes()

    def _create_tables(self):
        """Create all tables if not exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                language TEXT DEFAULT 'ar',
                country TEXT DEFAULT 'مصر',
                is_banned INTEGER DEFAULT 0,
                registered_at TEXT,
                last_active TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE,
                user_id INTEGER,
                order_type TEXT,
                order_data TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT UNIQUE,
                user_id INTEGER,
                ticket_type TEXT,
                status TEXT DEFAULT 'open',
                created_at TEXT,
                closed_at TEXT,
                assigned_admin INTEGER
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                sender_id INTEGER,
                message TEXT,
                created_at TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                admin_id INTEGER,
                ticket_id INTEGER,
                status TEXT DEFAULT 'active',
                started_at TEXT,
                ended_at TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                action TEXT,
                target_user INTEGER,
                order_number TEXT,
                details TEXT,
                timestamp TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                rating INTEGER,
                rating_type TEXT,
                comment TEXT,
                created_at TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS banned_users_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reason TEXT,
                banned_by INTEGER,
                banned_at TEXT,
                unbanned_at TEXT
            )
        ''')

        self.conn.commit()

    def _create_indexes(self):
        """Create indexes for better query performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_id ON users(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_users_lang ON users(language)",
            "CREATE INDEX IF NOT EXISTS idx_users_banned ON users(is_banned)",
            "CREATE INDEX IF NOT EXISTS idx_orders_number ON orders(order_number)",
            "CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
            "CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)",
            "CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket ON ticket_messages(ticket_id)",
            "CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_chat_sessions_status ON chat_sessions(status)",
            "CREATE INDEX IF NOT EXISTS idx_admin_logs_timestamp ON admin_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id)",
        ]
        for index in indexes:
            try:
                self.cursor.execute(index)
            except Exception:
                pass
        self.conn.commit()

    # ================= USERS =================
    def get_user_language(self, user_id: int) -> str:
        """Get user language preference"""
        try:
            self.cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
            row = self.cursor.fetchone()
            if row:
                return row['language']
            return 'ar'
        except Exception:
            return 'ar'

    def set_user_language(self, user_id: int, language: str) -> bool:
        """Set user language preference"""
        try:
            self.cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
            self.conn.commit()
            return True
        except Exception:
            return False

    def register_user(self, user_id: int, full_name: str, username: str, language: str = 'ar') -> bool:
        """Register a new user"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, full_name, username, language, registered_at, last_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, full_name, username, language, now, now))
            self.conn.commit()
            return True
        except Exception:
            return False

    def update_last_active(self, user_id: int) -> bool:
        """Update user last active timestamp"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('UPDATE users SET last_active = ? WHERE user_id = ?', (now, user_id))
            self.conn.commit()
            return True
        except Exception:
            return False

    def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        try:
            self.cursor.execute('SELECT is_banned FROM users WHERE user_id = ?', (user_id,))
            row = self.cursor.fetchone()
            return row and row['is_banned'] == 1
        except Exception:
            return False

    def is_banned(self, user_id: int) -> bool:
        """Alias for is_user_banned"""
        return self.is_user_banned(user_id)

    def ban_user(self, user_id: int, reason: str = None, banned_by: int = None) -> bool:
        """Ban a user"""
        try:
            self.cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                INSERT INTO banned_users_log (user_id, reason, banned_by, banned_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, reason, banned_by, now))
            self.conn.commit()
            return True
        except Exception:
            return False

    def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        try:
            self.cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                UPDATE banned_users_log SET unbanned_at = ? WHERE user_id = ? AND unbanned_at IS NULL
            ''', (now, user_id))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        try:
            self.cursor.execute('''
                SELECT full_name, username, language, country, is_banned, registered_at, last_active
                FROM users WHERE user_id = ?
            ''', (user_id,))
            row = self.cursor.fetchone()
            if row:
                return {
                    'name': row['full_name'],
                    'username': row['username'],
                    'lang': row['language'],
                    'country': row['country'],
                    'is_banned': row['is_banned'],
                    'registered_at': row['registered_at'],
                    'last_active': row['last_active']
                }
            return None
        except Exception:
            return None

    def get_all_users(self):
        """Get all users (legacy format)"""
        self.cursor.execute('SELECT user_id, full_name FROM users')
        return self.cursor.fetchall()

    def get_all_users_detailed(self) -> List[Dict]:
        """Get all users with details"""
        self.cursor.execute('''
            SELECT user_id, full_name, username, language, country, is_banned, registered_at, last_active
            FROM users ORDER BY registered_at DESC
        ''')
        return [dict(row) for row in self.cursor.fetchall()]

    def get_user_count(self) -> int:
        """Get total active user count"""
        try:
            self.cursor.execute('SELECT COUNT(*) FROM users WHERE is_banned = 0')
            return self.cursor.fetchone()[0]
        except Exception:
            return 0

    def get_stats(self) -> Dict:
        """Get bot statistics"""
        try:
            self.cursor.execute('SELECT COUNT(*) FROM users WHERE is_banned = 0')
            active = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM users WHERE is_banned = 1')
            banned = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM orders')
            total_orders = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM orders WHERE status = "pending"')
            pending_orders = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "open"')
            open_tickets = self.cursor.fetchone()[0]
            return {
                'active': active,
                'banned': banned,
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'open_tickets': open_tickets
            }
        except Exception:
            return {'active': 0, 'banned': 0, 'total_orders': 0, 'pending_orders': 0, 'open_tickets': 0}

    # ================= ORDERS =================
    def generate_order_number(self) -> str:
        """Generate unique order number"""
        return f"SC-{datetime.now(TIMEZONE).strftime('%Y%m%d%H%M%S')}"

    def create_order(self, user_id: int, order_type: str, order_data: str) -> Optional[str]:
        """Create a new order"""
        try:
            order_number = self.generate_order_number()
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                INSERT INTO orders (order_number, user_id, order_type, order_data, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'pending', ?, ?)
            ''', (order_number, user_id, order_type, order_data, now, now))
            self.conn.commit()
            return order_number
        except Exception:
            return None

    def get_order(self, order_number: str) -> Optional[Dict]:
        """Get order by number"""
        try:
            self.cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception:
            return None

    def update_order_status(self, order_number: str, status: str) -> bool:
        """Update order status"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                UPDATE orders SET status = ?, updated_at = ? WHERE order_number = ?
            ''', (status, now, order_number))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_pending_orders(self, limit: int = 50) -> List[Dict]:
        """Get pending orders"""
        try:
            self.cursor.execute('''
                SELECT * FROM orders WHERE status = 'pending' OR status = 'processing'
                ORDER BY created_at ASC LIMIT ?
            ''', (limit,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception:
            return []

    def get_all_orders(self) -> List[Dict]:
        """Get all orders"""
        try:
            self.cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception:
            return []

    # ================= TICKETS =================
    def generate_ticket_number(self) -> str:
        """Generate unique ticket number"""
        return f"TCK-{datetime.now(TIMEZONE).strftime('%Y%m%d%H%M%S')}"

    def create_ticket(self, user_id: int, ticket_type: str, message: str):
        """Create a support ticket"""
        try:
            ticket_number = self.generate_ticket_number()
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                INSERT INTO tickets (ticket_number, user_id, ticket_type, status, created_at)
                VALUES (?, ?, ?, 'open', ?)
            ''', (ticket_number, user_id, ticket_type, now))
            ticket_id = self.cursor.lastrowid
            self.cursor.execute('''
                INSERT INTO ticket_messages (ticket_id, sender_id, message, created_at)
                VALUES (?, ?, ?, ?)
            ''', (ticket_id, user_id, message, now))
            self.conn.commit()
            return ticket_number, ticket_id
        except Exception:
            return None, None

    def get_ticket(self, ticket_number: str) -> Optional[Dict]:
        """Get ticket by number"""
        try:
            self.cursor.execute('SELECT * FROM tickets WHERE ticket_number = ?', (ticket_number,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception:
            return None

    def get_ticket_by_id(self, ticket_id: int) -> Optional[Dict]:
        """Get ticket by ID"""
        try:
            self.cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception:
            return None

    def get_ticket_messages(self, ticket_id: int) -> List[Dict]:
        """Get all messages for a ticket"""
        try:
            self.cursor.execute('''
                SELECT sender_id, message, created_at FROM ticket_messages
                WHERE ticket_id = ? ORDER BY id ASC
            ''', (ticket_id,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception:
            return []

    def add_ticket_message(self, ticket_id: int, sender_id: int, message: str) -> bool:
        """Add message to ticket"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                INSERT INTO ticket_messages (ticket_id, sender_id, message, created_at)
                VALUES (?, ?, ?, ?)
            ''', (ticket_id, sender_id, message, now))
            self.conn.commit()
            return True
        except Exception:
            return False

    def update_ticket_status(self, ticket_number: str, status: str) -> bool:
        """Update ticket status"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                UPDATE tickets SET status = ?, updated_at = ? WHERE ticket_number = ?
            ''', (status, now, ticket_number))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_active_ticket_by_user(self, user_id: int):
        """Get active ticket for a specific user"""
        self.cursor.execute('''
            SELECT * FROM tickets 
            WHERE user_id = ? AND status IN ('open', 'processing')
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_open_tickets(self):
        """Get open tickets (legacy format)"""
        self.cursor.execute('''
            SELECT ticket_number, user_id, ticket_type, created_at
            FROM tickets WHERE status = "open" ORDER BY created_at DESC
        ''')
        return self.cursor.fetchall()

    def get_open_tickets_by_type(self, ticket_type: str) -> List[Dict]:
        """Get open tickets by type (includes open and processing)"""
        self.cursor.execute('''
            SELECT ticket_number, user_id, ticket_type, created_at
            FROM tickets 
            WHERE ticket_type = ? AND status IN ('open', 'processing')
            ORDER BY created_at DESC
        ''', (ticket_type,))
        return self.cursor.fetchall()

    def get_open_tickets_count(self) -> int:
        """Get count of open tickets"""
        self.cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "open"')
        return self.cursor.fetchone()[0]

    def close_ticket(self, ticket_number: str) -> bool:
        """Close a ticket"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                UPDATE tickets SET status = 'closed', closed_at = ? WHERE ticket_number = ?
            ''', (now, ticket_number))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_ticket_by_number(self, ticket_number: str):
        """Get ticket by number"""
        self.cursor.execute('SELECT * FROM tickets WHERE ticket_number = ?', (ticket_number,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None

    def update_ticket_status_by_id(self, ticket_id: int, status: str):
        """Update ticket status by ID"""
        now = datetime.now(TIMEZONE).isoformat()
        self.cursor.execute('''
            UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?
        ''', (status, now, ticket_id))
        self.conn.commit()

    # ================= CHAT =================
    def create_chat_session(self, user_id: int, admin_id: int, ticket_id: int) -> Optional[int]:
        """Create a new chat session"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                INSERT INTO chat_sessions (user_id, admin_id, ticket_id, status, started_at)
                VALUES (?, ?, ?, 'active', ?)
            ''', (user_id, admin_id, ticket_id, now))
            session_id = self.cursor.lastrowid
            self.conn.commit()
            return session_id
        except Exception:
            return None

    def get_active_chat(self, user_id: int) -> Optional[Dict]:
        """Get active chat session for user"""
        try:
            self.cursor.execute('''
                SELECT cs.*, t.ticket_number FROM chat_sessions cs
                JOIN tickets t ON cs.ticket_id = t.id
                WHERE cs.user_id = ? AND cs.status = 'active'
            ''', (user_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception:
            return None

    def get_chat_session(self, session_id: int) -> Optional[Dict]:
        """Get chat session by ID"""
        self.cursor.execute('''
            SELECT cs.*, t.ticket_number 
            FROM chat_sessions cs
            JOIN tickets t ON cs.ticket_id = t.id
            WHERE cs.id = ?
        ''', (session_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_active_chat_with_details(self, user_id: int) -> Optional[Dict]:
        """Get active chat session with details"""
        self.cursor.execute('''
            SELECT cs.*, t.ticket_number, t.ticket_type
            FROM chat_sessions cs
            JOIN tickets t ON cs.ticket_id = t.id
            WHERE cs.user_id = ? AND cs.status = 'active'
        ''', (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_active_chat_by_ticket(self, ticket_id: int):
        """Get active chat session by ticket ID"""
        self.cursor.execute('SELECT * FROM chat_sessions WHERE ticket_id = ? AND status = "active"', (ticket_id,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None

    def close_chat_session(self, session_id: int) -> bool:
        """Close a chat session"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                UPDATE chat_sessions SET status = 'closed', ended_at = ? WHERE id = ?
            ''', (now, session_id))
            self.conn.commit()
            return True
        except Exception:
            return False

    # ================= ADMIN =================
    def log_admin_action(self, admin_id: int, action: str, target_user: int = None,
                         order_number: str = None, details: str = None) -> bool:
        """Log admin action"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                INSERT INTO admin_logs (admin_id, action, target_user, order_number, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_id, action, target_user, order_number, details, now))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_admin_logs(self, limit: int = 50):
        """Get admin action logs (legacy format)"""
        self.cursor.execute('''
            SELECT admin_id, action, target_user, order_number, details, timestamp
            FROM admin_logs ORDER BY id DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    # ================= RATINGS (Updated) =================
    def save_rating(self, user_id: int, rating: int, rating_type: str = 'bot', comment: str = '') -> bool:
        """Save user rating"""
        try:
            now = datetime.now(TIMEZONE).isoformat()
            self.cursor.execute('''
                INSERT INTO ratings (user_id, rating, rating_type, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, rating, rating_type, comment, now))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Failed to save rating: {e}")
            return False

    def get_user_rating(self, user_id: int) -> Optional[Dict]:
        """Get user's last rating"""
        try:
            self.cursor.execute('''
                SELECT rating, rating_type, comment, created_at
                FROM ratings WHERE user_id = ? ORDER BY id DESC LIMIT 1
            ''', (user_id,))
            row = self.cursor.fetchone()
            if row:
                return {
                    'rating': row['rating'],
                    'type': row['rating_type'],
                    'comment': row['comment'],
                    'created_at': row['created_at']
                }
            return None
        except Exception:
            return None

    def get_all_ratings(self, limit: int = 100):
        """Get all ratings"""
        try:
            self.cursor.execute('''
                SELECT id, user_id, rating, rating_type, comment, created_at
                FROM ratings ORDER BY id DESC LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
        except Exception:
            return []

    def get_ratings_stats(self) -> Dict:
        """Get ratings statistics"""
        try:
            self.cursor.execute('SELECT COUNT(*) FROM ratings')
            total = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT AVG(rating) FROM ratings')
            avg = self.cursor.fetchone()[0] or 0
            self.cursor.execute('''
                SELECT rating, COUNT(*) as count 
                FROM ratings 
                GROUP BY rating 
                ORDER BY rating DESC
            ''')
            distribution = self.cursor.fetchall()
            return {
                'total': total,
                'average': round(avg, 2),
                'distribution': distribution
            }
        except Exception:
            return {'total': 0, 'average': 0, 'distribution': []}

    # ================= BANNED USERS =================
    def get_banned_users(self) -> List[Dict]:
        """Get list of banned users"""
        try:
            self.cursor.execute('''
                SELECT u.user_id, u.full_name, u.username, bl.reason, bl.banned_at
                FROM users u
                JOIN banned_users_log bl ON u.user_id = bl.user_id
                WHERE u.is_banned = 1 AND bl.unbanned_at IS NULL
                ORDER BY bl.banned_at DESC
            ''')
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception:
            return []

    # ================= DATABASE MANAGEMENT =================
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def commit(self):
        """Commit current transaction"""
        try:
            self.conn.commit()
        except Exception:
            pass

    def rollback(self):
        """Rollback current transaction"""
        try:
            self.conn.rollback()
        except Exception:
            pass


# Singleton instance
db = Database()