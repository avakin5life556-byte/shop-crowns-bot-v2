import sqlite3
import threading
import logging
import uuid
import random
import time
from datetime import datetime
from typing import Optional, Dict, List, Any, Union
import pytz

# فقط تعريف logger بدون basicConfig
logger = logging.getLogger(__name__)

TIMEZONE = pytz.timezone('Africa/Cairo')


class Database:
    _instance = None
    _lock = threading.Lock()
    _write_lock = threading.Lock()  # قفل خاص لعمليات الكتابة
    _read_lock = threading.Lock()   # قفل خاص لعمليات القراءة

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connection and create all tables"""
        try:
            self.conn = sqlite3.connect('shop_crowns.db', check_same_thread=False, timeout=30.0)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            # تفعيل الـ Foreign Keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute("PRAGMA journal_mode = WAL")  # تحسين الأداء والتزامن
            self.cursor.execute("PRAGMA busy_timeout = 30000")  # 30 ثانية timeout
            self._create_tables()
            self._create_indexes()
            self._migrate_tables()  # ترحيل الجداول القديمة
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _migrate_tables(self):
        """ترحيل الجداول القديمة لإضافة الأعمدة المفقودة"""
        try:
            # التحقق من وجود عمود updated_at في جدول tickets
            self.cursor.execute("PRAGMA table_info(tickets)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column to tickets table")
                self.cursor.execute('ALTER TABLE tickets ADD COLUMN updated_at TEXT')
                # تحديث القيم القديمة
                self.cursor.execute('UPDATE tickets SET updated_at = created_at WHERE updated_at IS NULL')
                self.conn.commit()
        except Exception as e:
            logger.error(f"Migration error: {e}")

    def _create_tables(self):
        """Create all tables if not exist with Foreign Keys"""
        
        # جدول المستخدمين
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
        
        # جدول الطلبات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE,
                user_id INTEGER,
                order_type TEXT,
                order_data TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # جدول التذاكر - تم إضافة updated_at
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT UNIQUE,
                user_id INTEGER,
                ticket_type TEXT,
                status TEXT DEFAULT 'open',
                created_at TEXT,
                updated_at TEXT,
                closed_at TEXT,
                assigned_admin INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # جدول رسائل التذاكر
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                sender_id INTEGER,
                message TEXT,
                created_at TEXT,
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
                FOREIGN KEY (sender_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول جلسات المحادثة
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                admin_id INTEGER,
                ticket_id INTEGER,
                status TEXT DEFAULT 'active',
                started_at TEXT,
                ended_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (admin_id) REFERENCES users(user_id),
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
            )
        ''')
        
        # جدول سجلات الأدمن
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                action TEXT,
                target_user INTEGER,
                order_number TEXT,
                details TEXT,
                timestamp TEXT,
                FOREIGN KEY (admin_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول التقييمات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                rating INTEGER,
                rating_type TEXT,
                comment TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # جدول سجل المحظورين
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS banned_users_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reason TEXT,
                banned_by INTEGER,
                banned_at TEXT,
                unbanned_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (banned_by) REFERENCES users(user_id)
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
            except Exception as e:
                logger.warning(f"Failed to create index {index}: {e}")
        self.conn.commit()

    def _execute_write(self, query: str, params: tuple = (), max_retries: int = 3) -> bool:
        """تنفيذ عمليات الكتابة مع قفل وآلية إعادة المحاولة"""
        for attempt in range(max_retries):
            try:
                with self._write_lock:
                    self.cursor.execute(query, params)
                    self.conn.commit()
                    return True
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))  # انتظار تصاعدي
                    continue
                logger.error(f"Write operation failed (attempt {attempt + 1}): {e} | Query: {query}")
                self.conn.rollback()
                return False
            except Exception as e:
                logger.error(f"Write operation failed: {e} | Query: {query}")
                self.conn.rollback()
                return False
        return False

    def _execute_read(self, query: str, params: tuple = (), fetch_one: bool = False) -> Union[Any, List, None]:
        """تنفيذ عمليات القراءة مع قفل"""
        with self._read_lock:
            try:
                self.cursor.execute(query, params)
                if fetch_one:
                    return self.cursor.fetchone()
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Read operation failed: {e} | Query: {query}")
                return None if fetch_one else []

    # ================= USERS =================
    def get_user_language(self, user_id: int) -> str:
        """Get user language preference"""
        result = self._execute_read(
            'SELECT language FROM users WHERE user_id = ?',
            (user_id,), fetch_one=True
        )
        if result:
            return result['language']
        return 'ar'

    def set_user_language(self, user_id: int, language: str) -> bool:
        """Set user language preference"""
        return self._execute_write(
            'UPDATE users SET language = ? WHERE user_id = ?',
            (language, user_id)
        )

    def register_user(self, user_id: int, full_name: str, username: str, language: str = 'ar') -> bool:
        """Register a new user"""
        now = datetime.now(TIMEZONE).isoformat()
        return self._execute_write('''
            INSERT OR IGNORE INTO users (user_id, full_name, username, language, registered_at, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, full_name, username, language, now, now))

    def update_last_active(self, user_id: int) -> bool:
        """Update user last active timestamp"""
        now = datetime.now(TIMEZONE).isoformat()
        return self._execute_write(
            'UPDATE users SET last_active = ? WHERE user_id = ?',
            (now, user_id)
        )

    def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        result = self._execute_read(
            'SELECT is_banned FROM users WHERE user_id = ?',
            (user_id,), fetch_one=True
        )
        return result and result['is_banned'] == 1

    def is_banned(self, user_id: int) -> bool:
        """Alias for is_user_banned"""
        return self.is_user_banned(user_id)

    def ban_user(self, user_id: int, reason: str = None, banned_by: int = None) -> bool:
        """Ban a user"""
        with self._write_lock:
            try:
                self.cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
                now = datetime.now(TIMEZONE).isoformat()
                self.cursor.execute('''
                    INSERT INTO banned_users_log (user_id, reason, banned_by, banned_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, reason, banned_by, now))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Ban user failed: {e}")
                self.conn.rollback()
                return False

    def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        with self._write_lock:
            try:
                self.cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
                now = datetime.now(TIMEZONE).isoformat()
                self.cursor.execute('''
                    UPDATE banned_users_log SET unbanned_at = ? 
                    WHERE user_id = ? AND unbanned_at IS NULL
                ''', (now, user_id))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Unban user failed: {e}")
                self.conn.rollback()
                return False

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        result = self._execute_read('''
            SELECT full_name, username, language, country, is_banned, registered_at, last_active
            FROM users WHERE user_id = ?
        ''', (user_id,), fetch_one=True)
        
        if result:
            return {
                'name': result['full_name'],
                'username': result['username'],
                'lang': result['language'],
                'country': result['country'],
                'is_banned': result['is_banned'],
                'registered_at': result['registered_at'],
                'last_active': result['last_active']
            }
        return None

    def get_all_users(self):
        """Get all users (legacy format)"""
        return self._execute_read('SELECT user_id, full_name FROM users')

    def get_all_users_detailed(self) -> List[Dict]:
        """Get all users with details"""
        results = self._execute_read('''
            SELECT user_id, full_name, username, language, country, is_banned, registered_at, last_active
            FROM users ORDER BY registered_at DESC
        ''')
        return [dict(row) for row in results] if results else []

    def get_user_count(self) -> int:
        """Get total active user count"""
        result = self._execute_read(
            'SELECT COUNT(*) FROM users WHERE is_banned = 0',
            fetch_one=True
        )
        return result[0] if result else 0

    def get_stats(self) -> Dict:
        """Get bot statistics"""
        try:
            active = self._execute_read('SELECT COUNT(*) FROM users WHERE is_banned = 0', fetch_one=True)
            banned = self._execute_read('SELECT COUNT(*) FROM users WHERE is_banned = 1', fetch_one=True)
            total_orders = self._execute_read('SELECT COUNT(*) FROM orders', fetch_one=True)
            pending_orders = self._execute_read('SELECT COUNT(*) FROM orders WHERE status = "pending"', fetch_one=True)
            open_tickets = self._execute_read('SELECT COUNT(*) FROM tickets WHERE status = "open"', fetch_one=True)
            
            return {
                'active': active[0] if active else 0,
                'banned': banned[0] if banned else 0,
                'total_orders': total_orders[0] if total_orders else 0,
                'pending_orders': pending_orders[0] if pending_orders else 0,
                'open_tickets': open_tickets[0] if open_tickets else 0
            }
        except Exception as e:
            logger.error(f"Get stats failed: {e}")
            return {'active': 0, 'banned': 0, 'total_orders': 0, 'pending_orders': 0, 'open_tickets': 0}

    # ================= ORDERS =================
    def generate_order_number(self) -> str:
        """Generate unique order number with UUID and timestamp"""
        short_uuid = str(uuid.uuid4())[:8]
        timestamp = datetime.now(TIMEZONE).strftime('%Y%m%d%H%M%S%f')[:-3]
        return f"SC-{timestamp}-{short_uuid}"

    def create_order(self, user_id: int, order_type: str, order_data: str) -> Optional[str]:
        """Create a new order with unique order number"""
        max_retries = 3
        for attempt in range(max_retries):
            order_number = self.generate_order_number()
            now = datetime.now(TIMEZONE).isoformat()
            
            with self._write_lock:
                try:
                    self.cursor.execute('''
                        INSERT INTO orders (order_number, user_id, order_type, order_data, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, 'pending', ?, ?)
                    ''', (order_number, user_id, order_type, order_data, now, now))
                    self.conn.commit()
                    return order_number
                except sqlite3.IntegrityError:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to generate unique order number after {max_retries} attempts")
                        return None
                    continue
                except Exception as e:
                    logger.error(f"Create order failed: {e}")
                    return None
        return None

    def get_order(self, order_number: str) -> Optional[Dict]:
        """Get order by number"""
        result = self._execute_read(
            'SELECT * FROM orders WHERE order_number = ?',
            (order_number,), fetch_one=True
        )
        return dict(result) if result else None

    def update_order_status(self, order_number: str, status: str) -> bool:
        """Update order status"""
        now = datetime.now(TIMEZONE).isoformat()
        return self._execute_write('''
            UPDATE orders SET status = ?, updated_at = ? WHERE order_number = ?
        ''', (status, now, order_number))

    def get_pending_orders(self, limit: int = 50) -> List[Dict]:
        """Get pending orders"""
        results = self._execute_read('''
            SELECT * FROM orders WHERE status = 'pending' OR status = 'processing'
            ORDER BY created_at ASC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in results] if results else []

    def get_all_orders(self) -> List[Dict]:
        """Get all orders"""
        results = self._execute_read('SELECT * FROM orders ORDER BY created_at DESC')
        return [dict(row) for row in results] if results else []

    # ================= TICKETS =================
    def generate_ticket_number(self) -> str:
        """Generate unique ticket number with UUID"""
        short_uuid = str(uuid.uuid4())[:6]
        timestamp = datetime.now(TIMEZONE).strftime('%Y%m%d%H%M%S%f')[:-3]
        return f"TCK-{timestamp}-{short_uuid}"

    def create_ticket(self, user_id: int, ticket_type: str, message: str):
        """Create a support ticket"""
        ticket_number = self.generate_ticket_number()
        now = datetime.now(TIMEZONE).isoformat()
        
        with self._write_lock:
            try:
                self.cursor.execute('''
                    INSERT INTO tickets (ticket_number, user_id, ticket_type, status, created_at, updated_at)
                    VALUES (?, ?, ?, 'open', ?, ?)
                ''', (ticket_number, user_id, ticket_type, now, now))
                ticket_id = self.cursor.lastrowid
                self.cursor.execute('''
                    INSERT INTO ticket_messages (ticket_id, sender_id, message, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (ticket_id, user_id, message, now))
                self.conn.commit()
                return ticket_number, ticket_id
            except Exception as e:
                logger.error(f"Create ticket failed: {e}")
                self.conn.rollback()
                return None, None

    # الدالة الأساسية للحصول على تذكرة برقمها
    def _get_ticket_by_number(self, ticket_number: str) -> Optional[Dict]:
        """Internal method to get ticket by number"""
        result = self._execute_read(
            'SELECT * FROM tickets WHERE ticket_number = ?',
            (ticket_number,), fetch_one=True
        )
        return dict(result) if result else None

    def get_ticket(self, ticket_number: str) -> Optional[Dict]:
        """Get ticket by number"""
        return self._get_ticket_by_number(ticket_number)

    def get_ticket_by_id(self, ticket_id: int) -> Optional[Dict]:
        """Get ticket by ID"""
        result = self._execute_read(
            'SELECT * FROM tickets WHERE id = ?',
            (ticket_id,), fetch_one=True
        )
        return dict(result) if result else None

    def get_ticket_messages(self, ticket_id: int) -> List[Dict]:
        """Get all messages for a ticket"""
        results = self._execute_read('''
            SELECT sender_id, message, created_at FROM ticket_messages
            WHERE ticket_id = ? ORDER BY id ASC
        ''', (ticket_id,))
        return [dict(row) for row in results] if results else []

    def add_ticket_message(self, ticket_id: int, sender_id: int, message: str) -> bool:
        """Add message to ticket"""
        now = datetime.now(TIMEZONE).isoformat()
        return self._execute_write('''
            INSERT INTO ticket_messages (ticket_id, sender_id, message, created_at)
            VALUES (?, ?, ?, ?)
        ''', (ticket_id, sender_id, message, now))

    def update_ticket_status(self, ticket_number: str, status: str) -> bool:
        """Update ticket status"""
        now = datetime.now(TIMEZONE).isoformat()
        return self._execute_write('''
            UPDATE tickets SET status = ?, updated_at = ? WHERE ticket_number = ?
        ''', (status, now, ticket_number))

    def get_active_ticket_by_user(self, user_id: int):
        """Get active ticket for a specific user"""
        result = self._execute_read('''
            SELECT * FROM tickets 
            WHERE user_id = ? AND status IN ('open', 'processing')
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,), fetch_one=True)
        return dict(result) if result else None

    def get_open_tickets(self):
        """Get open tickets (legacy format)"""
        return self._execute_read('''
            SELECT ticket_number, user_id, ticket_type, created_at
            FROM tickets WHERE status = "open" ORDER BY created_at DESC
        ''')

    def get_open_tickets_by_type(self, ticket_type: str) -> List[Dict]:
        """Get open tickets by type (includes open and processing)"""
        results = self._execute_read('''
            SELECT ticket_number, user_id, ticket_type, created_at
            FROM tickets 
            WHERE ticket_type = ? AND status IN ('open', 'processing')
            ORDER BY created_at DESC
        ''', (ticket_type,))
        return [dict(row) for row in results] if results else []

    def get_open_tickets_count(self) -> int:
        """Get count of open tickets"""
        result = self._execute_read(
            'SELECT COUNT(*) FROM tickets WHERE status = "open"',
            fetch_one=True
        )
        return result[0] if result else 0

    def close_ticket(self, ticket_number: str) -> bool:
        """Close a ticket"""
        now = datetime.now(TIMEZONE).isoformat()
        return self._execute_write('''
            UPDATE tickets SET status = 'closed', closed_at = ?, updated_at = ? 
            WHERE ticket_number = ?
        ''', (now, now, ticket_number))

    # Alias للدالة الأساسية - متوافقة مع الكود القديم
    def get_ticket_by_number(self, ticket_number: str):
        """Get ticket by number (alias for get_ticket)"""
        return self.get_ticket(ticket_number)

    def update_ticket_status_by_id(self, ticket_id: int, status: str):
        """Update ticket status by ID"""
        now = datetime.now(TIMEZONE).isoformat()
        self._execute_write('''
            UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?
        ''', (status, now, ticket_id))

    # ================= CHAT =================
    def create_chat_session(self, user_id: int, admin_id: int, ticket_id: int) -> Optional[int]:
        """Create a new chat session"""
        now = datetime.now(TIMEZONE).isoformat()
        with self._write_lock:
            try:
                self.cursor.execute('''
                    INSERT INTO chat_sessions (user_id, admin_id, ticket_id, status, started_at)
                    VALUES (?, ?, ?, 'active', ?)
                ''', (user_id, admin_id, ticket_id, now))
                session_id = self.cursor.lastrowid
                self.conn.commit()
                return session_id
            except Exception as e:
                logger.error(f"Create chat session failed: {e}")
                self.conn.rollback()
                return None

    def get_active_chat(self, user_id: int) -> Optional[Dict]:
        """Get active chat session for user"""
        result = self._execute_read('''
            SELECT cs.*, t.ticket_number FROM chat_sessions cs
            JOIN tickets t ON cs.ticket_id = t.id
            WHERE cs.user_id = ? AND cs.status = 'active'
        ''', (user_id,), fetch_one=True)
        return dict(result) if result else None

    def get_chat_session(self, session_id: int) -> Optional[Dict]:
        """Get chat session by ID"""
        result = self._execute_read('''
            SELECT cs.*, t.ticket_number 
            FROM chat_sessions cs
            JOIN tickets t ON cs.ticket_id = t.id
            WHERE cs.id = ?
        ''', (session_id,), fetch_one=True)
        return dict(result) if result else None

    def get_active_chat_with_details(self, user_id: int) -> Optional[Dict]:
        """Get active chat session with details"""
        result = self._execute_read('''
            SELECT cs.*, t.ticket_number, t.ticket_type
            FROM chat_sessions cs
            JOIN tickets t ON cs.ticket_id = t.id
            WHERE cs.user_id = ? AND cs.status = 'active'
        ''', (user_id,), fetch_one=True)
        return dict(result) if result else None

    def get_active_chat_by_ticket(self, ticket_id: int):
        """Get active chat session by ticket ID"""
        result = self._execute_read(
            'SELECT * FROM chat_sessions WHERE ticket_id = ? AND status = "active"',
            (ticket_id,), fetch_one=True
        )
        return dict(result) if result else None

    def close_chat_session(self, session_id: int) -> bool:
        """Close a chat session"""
        now = datetime.now(TIMEZONE).isoformat()
        return self._execute_write('''
            UPDATE chat_sessions SET status = 'closed', ended_at = ? WHERE id = ?
        ''', (now, session_id))

    # ================= ADMIN =================
    def log_admin_action(self, admin_id: int, action: str, target_user: int = None,
                         order_number: str = None, details: str = None) -> bool:
        """Log admin action"""
        now = datetime.now(TIMEZONE).isoformat()
        return self._execute_write('''
            INSERT INTO admin_logs (admin_id, action, target_user, order_number, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (admin_id, action, target_user, order_number, details, now))

    def get_admin_logs(self, limit: int = 50):
        """Get admin action logs (legacy format)"""
        return self._execute_read('''
            SELECT admin_id, action, target_user, order_number, details, timestamp
            FROM admin_logs ORDER BY id DESC LIMIT ?
        ''', (limit,))

    # ================= RATINGS =================
    def save_rating(self, user_id: int, rating: int, rating_type: str = 'bot', comment: str = '') -> bool:
        """Save user rating"""
        now = datetime.now(TIMEZONE).isoformat()
        return self._execute_write('''
            INSERT INTO ratings (user_id, rating, rating_type, comment, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, rating, rating_type, comment, now))

    def get_user_rating(self, user_id: int) -> Optional[Dict]:
        """Get user's last rating"""
        result = self._execute_read('''
            SELECT rating, rating_type, comment, created_at
            FROM ratings WHERE user_id = ? ORDER BY id DESC LIMIT 1
        ''', (user_id,), fetch_one=True)
        
        if result:
            return {
                'rating': result['rating'],
                'type': result['rating_type'],
                'comment': result['comment'],
                'created_at': result['created_at']
            }
        return None

    def get_all_ratings(self, limit: int = 100):
        """Get all ratings"""
        return self._execute_read('''
            SELECT id, user_id, rating, rating_type, comment, created_at
            FROM ratings ORDER BY id DESC LIMIT ?
        ''', (limit,))

    def get_ratings_stats(self) -> Dict:
        """Get ratings statistics"""
        try:
            total_result = self._execute_read('SELECT COUNT(*) FROM ratings', fetch_one=True)
            avg_result = self._execute_read('SELECT AVG(rating) FROM ratings', fetch_one=True)
            distribution = self._execute_read('''
                SELECT rating, COUNT(*) as count 
                FROM ratings 
                GROUP BY rating 
                ORDER BY rating DESC
            ''')
            
            total = total_result[0] if total_result else 0
            avg = avg_result[0] if avg_result and avg_result[0] is not None else 0
            
            return {
                'total': total,
                'average': round(avg, 2),
                'distribution': distribution if distribution else []
            }
        except Exception as e:
            logger.error(f"Get ratings stats failed: {e}")
            return {'total': 0, 'average': 0, 'distribution': []}

    # ================= BANNED USERS =================
    def get_banned_users(self) -> List[Dict]:
        """Get list of banned users"""
        results = self._execute_read('''
            SELECT u.user_id, u.full_name, u.username, bl.reason, bl.banned_at
            FROM users u
            JOIN banned_users_log bl ON u.user_id = bl.user_id
            WHERE u.is_banned = 1 AND bl.unbanned_at IS NULL
            ORDER BY bl.banned_at DESC
        ''')
        return [dict(row) for row in results] if results else []

    # ================= DATABASE MANAGEMENT =================
    def close(self):
        """Close database connection"""
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                logger.error(f"Error closing database: {e}")

    def commit(self):
        """Commit current transaction"""
        try:
            self.conn.commit()
        except Exception as e:
            logger.error(f"Commit failed: {e}")

    def rollback(self):
        """Rollback current transaction"""
        try:
            self.conn.rollback()
        except Exception as e:
            logger.error(f"Rollback failed: {e}")


# Singleton instance
db = Database()
