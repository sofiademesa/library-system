# =============================================================
# CORE MODULE — Stacked Knowledge: A Library System
# This is the main backend file of the library system.

# For the core logic and more comprehensive implementation of OOP principles, event-driven programming, parallel programming,
# memory management, and more, please refer to 'library.py'. 

# Similarly, Database interactions and queries are also handled in 'library.py'.
# Please refer to those file when grading the technical and database portion of the project.

# The GUI version of this system is in 'library_gui.py'.

# REQUIREMENTS:
# 1. Install dependencies via terminal/command prompt:  pip install mysql-connector-python
# 2. XAMPP must be running with MySQL enabled.
# 3. Database 'library_db' will be auto-created on first run.
# =============================================================

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import hashlib
import gc
import multiprocessing
import os
import time

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("\nWARNING: mysql-connector-python is not installed.")
    print("  Install it with:  pip install mysql-connector-python")
    print("  Using fallback mode for now...\n")

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "",
    "database": "library_db",
}

MAX_BORROW  = 5
FEE_PER_DAY = 50
BORROW_DAYS = 7

DEWEY_CATEGORIES = {
    "000": "General Knowledge", "100": "Philosophy",  "200": "Religion",
    "300": "Social Sciences",   "400": "Language",     "500": "Science",
    "600": "Technology",        "700": "Arts",         "800": "Literature",
    "900": "History"
}

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def line():
    print("-" * 75)


# PARALLEL PROCESSING WORKERS
def _worker_fee_summary(users, result_queue):
    total_fees = sum(u.total_fees for u in users)
    users_with_fees = [(u.username, u.total_fees) for u in users if u.total_fees > 0]
    result_queue.put(("fee_summary", total_fees, users_with_fees))

def _worker_overdue_report(users, result_queue):
    overdue = [
        (u.username, r.title, r.due_on.strftime("%Y-%m-%d"), r.overdue_fee())
        for u in users
        for r in u.borrowed
        if r.overdue_fee() > 0
    ]
    result_queue.put(("overdue_report", overdue))

def _worker_book_availability(books, result_queue):
    total_titles  = len(books)
    total_copies  = sum(b.total for b in books)
    available_now = sum(b.available for b in books)
    on_waitlist   = sum(len(b.waitlist) for b in books)
    unavailable   = [(b.title, b.total - b.available, b.total) for b in books if b.available == 0]
    result_queue.put(("book_availability", total_titles, total_copies, available_now, on_waitlist, unavailable))

def run_parallel_tasks(lib):
    users        = lib.users
    books        = lib.books
    result_queue = multiprocessing.Queue()

    processes = [
        multiprocessing.Process(target=_worker_fee_summary,       args=(users, result_queue)),
        multiprocessing.Process(target=_worker_overdue_report,    args=(users, result_queue)),
        multiprocessing.Process(target=_worker_book_availability, args=(books, result_queue)),
    ]

    print("\n" + "=" * 75)
    print("  OPAC Parallel Report Generation — Starting 3 processes...")
    print("=" * 75)
    start = time.time()

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    elapsed = time.time() - start
    reports = {}
    while not result_queue.empty():
        item = result_queue.get()
        reports[item[0]] = item[1:]

    print(f"\n  All reports generated in {elapsed:.2f}s")
    line()

    if "fee_summary" in reports:
        total_fees, users_with_fees = reports["fee_summary"]
        print("  FEE SUMMARY")
        if users_with_fees:
            for username, fee in users_with_fees:
                print(f"    {username:<15} P{fee}")
        else:
            print("    No outstanding fees.")
        print(f"    Total owed: P{total_fees}")
        line()

    if "overdue_report" in reports:
        overdue = reports["overdue_report"][0]
        print("  OVERDUE BOOKS")
        if overdue:
            for username, title, due, fee in overdue:
                print(f"    {username:<12} '{title[:20]}' due {due} | P{fee}")
        else:
            print("    No overdue books.")
        line()

    if "book_availability" in reports:
        total_titles, total_copies, available_now, on_waitlist, unavailable = reports["book_availability"]
        print("  BOOK AVAILABILITY")
        print(f"    Total titles   : {total_titles}")
        print(f"    Total copies   : {total_copies}")
        print(f"    Available now  : {available_now}")
        print(f"    On waitlist    : {on_waitlist}")
        if unavailable:
            print(f"    Fully borrowed :")
            for title, borrowed, total in unavailable:
                print(f"      '{title[:25]}' ({borrowed}/{total} out)")
        else:
            print(f"    Fully borrowed : None")
        line()

    input("\n  Press Enter to continue...")


# DATABASE LAYER
class Database:
    def __init__(self, config: dict):
        self._config = config
        self.conn    = None
        if MYSQL_AVAILABLE:
            self._connect_and_init()
        else:
            print("  [DB] MySQL not available. Database operations disabled.")
            self.conn = None
            return

    def _connect_and_init(self):
        cfg     = self._config.copy()
        db_name = cfg.pop("database")
        try:
            tmp = mysql.connector.connect(**cfg)
            cur = tmp.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            tmp.commit()
            cur.close()
            tmp.close()
        except MySQLError as e:
            print(f"  [DB] Could not create database '{db_name}': {e}")
            raise

        try:
            self.conn = mysql.connector.connect(database=db_name, **cfg)
            self.conn.autocommit = True
            self._init_schema()
        except MySQLError as e:
            print(f"  [DB] Connection failed: {e}")
            raise

    def _init_schema(self):
        ddl = [
            """CREATE TABLE IF NOT EXISTS books (
                id        INT           NOT NULL AUTO_INCREMENT,
                title     VARCHAR(255)  NOT NULL,
                author    VARCHAR(255)  NOT NULL,
                dewey     CHAR(3)       NOT NULL DEFAULT '000',
                total     INT           NOT NULL DEFAULT 1,
                available INT           NOT NULL DEFAULT 1,
                year      SMALLINT,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB""",

            """CREATE TABLE IF NOT EXISTS users (
                username      VARCHAR(50)    NOT NULL,
                password_hash CHAR(64)       NOT NULL,
                active        TINYINT(1)     NOT NULL DEFAULT 1,
                paid          DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
                PRIMARY KEY (username)
            ) ENGINE=InnoDB""",

            """CREATE TABLE IF NOT EXISTS borrow_records (
                id          INT            NOT NULL AUTO_INCREMENT,
                username    VARCHAR(50)    NOT NULL,
                book_id     INT            NOT NULL,
                book_title  VARCHAR(255)   NOT NULL,
                borrowed_on DATETIME       NOT NULL,
                due_on      DATETIME       NOT NULL,
                returned_on DATETIME,
                fee         DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
                PRIMARY KEY (id),
                INDEX idx_user (username),
                INDEX idx_book (book_id)
            ) ENGINE=InnoDB""",

            """CREATE TABLE IF NOT EXISTS waitlist (
                book_id  INT         NOT NULL,
                username VARCHAR(50) NOT NULL,
                position INT         NOT NULL,
                PRIMARY KEY (book_id, username)
            ) ENGINE=InnoDB""",

            """CREATE TABLE IF NOT EXISTS payments (
                id       INT            NOT NULL AUTO_INCREMENT,
                username VARCHAR(50)    NOT NULL,
                amount   DECIMAL(10,2)  NOT NULL,
                paid_on  DATETIME       NOT NULL,
                PRIMARY KEY (id),
                INDEX idx_user (username)
            ) ENGINE=InnoDB""",
        ]
        cur = self.conn.cursor()
        for stmt in ddl:
            cur.execute(stmt)
        cur.close()

    def _reconnect_if_needed(self):
        if not MYSQL_AVAILABLE or not self.conn:
            return
        try:
            self.conn.ping(reconnect=True, attempts=3, delay=1)
        except MySQLError:
            cfg = self._config.copy()
            self.conn = mysql.connector.connect(**cfg)
            self.conn.autocommit = True

    def execute(self, sql: str, params=None):
        if not MYSQL_AVAILABLE or not self.conn:
            return None
        self._reconnect_if_needed()
        cur = self.conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur

    def fetchall(self, sql: str, params=None) -> list:
        cur = self.execute(sql, params)
        if cur is None:
            return []
        rows = cur.fetchall()
        cur.close()
        return rows

    def fetchone(self, sql: str, params=None):
        cur = self.execute(sql, params)
        if cur is None:
            return None
        row = cur.fetchone()
        cur.close()
        return row


# EVENT DISPATCHER
class EventDispatcher:
    def __init__(self):
        self._handlers: dict[str, list] = {}

    def register(self, event: str, handler):
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, *args):
        handlers = self._handlers.get(event, [])
        if not handlers:
            print(f"  [Event] No handler for event: '{event}'")
            return
        for handler in handlers:
            handler(*args)


# DOMAIN CLASSES
class Person(ABC):
    def __init__(self, username, password, pre_hashed=False):
        self.username = username
        self._pw      = password if pre_hashed else hash_pw(password)

    def check_password(self, password):
        return self._pw == hash_pw(password)

    @abstractmethod
    def view_dashboard(self):
        pass


class Book:
    _next_id = 1

    def __init__(self, title, author, dewey, copies=1, year=None, book_id=None):
        if book_id is not None:
            self.id = book_id
        else:
            self.id        = Book._next_id
            Book._next_id += 1
        self.title     = title
        self.author    = author
        self.dewey     = dewey if dewey in DEWEY_CATEGORIES else "000"
        self.total     = copies
        self.available = copies
        self.waitlist  = []
        self.year      = year


class BorrowRecord:
    def __init__(self, book):
        self.record_id   = None
        self.book        = book
        self.title       = book.title
        self.book_id     = book.id
        self.borrowed_on = datetime.now()
        self.due_on      = self.borrowed_on + timedelta(days=BORROW_DAYS)
        self.returned_on = None
        self.fee         = 0

    def overdue_fee(self):
        if not self.returned_on and datetime.now() > self.due_on:
            return (datetime.now() - self.due_on).days * FEE_PER_DAY
        return 0

    def do_return(self):
        """Marks the book as returned, locks in the fee, restores availability.
        Waitlist handling (pop + DB cleanup + auto-borrow) is done in User.return_book()
        so it has access to the db reference and the full user_map."""
        self.returned_on = datetime.now()
        self.fee = self.overdue_fee()
        if self.book:
            self.book.available += 1
            # NOTE: waitlist notification + auto-borrow handled in User.return_book()
            self.book = None


class User(Person):
    def __init__(self, username, password, db=None, pre_hashed=False):
        super().__init__(username, password, pre_hashed=pre_hashed)
        self.db       = db
        self.active   = True
        self.borrowed = []
        self.history  = []
        self.paid     = 0
        # list of Book objects the user is currently on the waitlist for
        self.waitlisted = []

    def __getstate__(self):
        state = self.__dict__.copy()
        state["db"] = None
        return state

    def __setstate__(self, state):
        state.setdefault("db", None)
        state.setdefault("waitlisted", [])
        self.__dict__.update(state)

    @property
    def total_fees(self):
        owed = (sum(r.overdue_fee() for r in self.borrowed)
                + sum(r.fee for r in self.history))
        return max(0, owed - self.paid)

    def borrow_book(self, book):
        """Borrow a book. If unavailable, offers to join the waitlist."""
        if book is None:
            print("Book not found."); return
        if len(self.borrowed) >= MAX_BORROW:
            print(f"Borrow limit reached ({MAX_BORROW} books max)."); return
        if self.total_fees > 0:
            print(f"Please settle your fees first: P{self.total_fees}"); return
        if book.available <= 0:
            print("Book is not available.")
            ans = input("Join waitlist? (yes/no): ").strip().lower()
            if ans == "yes":
                self._join_waitlist(book)
            return

        self._do_borrow(book)

    def _do_borrow(self, book):
        """Internal: creates the BorrowRecord, updates DB, decrements availability."""
        record = BorrowRecord(book)
        self.borrowed.append(record)
        book.available -= 1

        if self.db:
            cur = self.db.execute(
                "INSERT INTO borrow_records "
                "(username, book_id, book_title, borrowed_on, due_on) "
                "VALUES (%s, %s, %s, %s, %s)",
                (self.username, book.id, book.title,
                 record.borrowed_on, record.due_on)
            )
            record.record_id = cur.lastrowid
            cur.close()
            self.db.execute(
                "UPDATE books SET available = %s WHERE id = %s",
                (book.available, book.id)
            )

        print(f"Borrowed '{book.title}' | Due: {record.due_on.strftime('%Y-%m-%d')}")
        return record

    def _join_waitlist(self, book):
        """Add this user to a book's waitlist (in-memory + DB)."""
        if self in book.waitlist:
            print("You're already on the waitlist.")
            return
        book.waitlist.append(self)
        pos = book.waitlist.index(self)
        self.waitlisted.append(book)   # track on the user side too

        if self.db:
            self.db.execute(
                "INSERT INTO waitlist (book_id, username, position) "
                "VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE position = VALUES(position)",
                (book.id, self.username, pos)
            )
        print(f"Added to waitlist for '{book.title}'. Position: {pos + 1}")

    def return_book(self, book_id):
        """Return a borrowed book. After restoring availability, check the waitlist:
        - Remove the first waiting user from the list
        - Clean up their DB waitlist row                  (FIX 2)
        - Re-number remaining waitlist positions in DB    (FIX 2)
        - Auto-create a BorrowRecord for them             (FIX 1)
        """
        record = next((r for r in self.borrowed if r.book_id == book_id), None)
        if not record:
            print("No active borrow found for that ID."); return

        book = record.book         
        record.do_return()
        self.borrowed.remove(record)
        self.history.append(record)

        # Persist return to DB
        if self.db:
            self.db.execute(
                "UPDATE borrow_records SET returned_on = %s, fee = %s WHERE id = %s",
                (record.returned_on, record.fee, record.record_id)
            )
            if book:
                self.db.execute(
                    "UPDATE books SET available = %s WHERE id = %s",
                    (book.available, book.id)
                )

        print(f"Returned '{record.title}' | Fee: P{record.fee}")

        if book and book.waitlist:
            next_user = book.waitlist.pop(0)   # first in line

            # Remove from the next_user's personal waitlisted list
            if book in next_user.waitlisted:
                next_user.waitlisted.remove(book)

            if self.db:
                self.db.execute(
                    "DELETE FROM waitlist WHERE book_id = %s AND username = %s",
                    (book.id, next_user.username)
                )
                for pos, waiting_user in enumerate(book.waitlist):
                    self.db.execute(
                        "INSERT INTO waitlist (book_id, username, position) "
                        "VALUES (%s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE position = VALUES(position)",
                        (book.id, waiting_user.username, pos)
                    )

            if (len(next_user.borrowed) < MAX_BORROW and next_user.total_fees == 0):
                print(f"[Waitlist] Auto-borrowing '{book.title}' for {next_user.username}!")
                next_user._do_borrow(book)
            else:
                book.waitlist.insert(0, next_user)
                next_user.waitlisted.append(book)
                if self.db:
                    for pos, waiting_user in enumerate(book.waitlist):
                        self.db.execute(
                            "INSERT INTO waitlist (book_id, username, position) "
                            "VALUES (%s, %s, %s) "
                            "ON DUPLICATE KEY UPDATE position = VALUES(position)",
                            (book.id, waiting_user.username, pos)
                        )
                reason = "borrow limit reached" if len(next_user.borrowed) >= MAX_BORROW else "outstanding fees"
                print(f"[Waitlist] Could not auto-borrow for {next_user.username} ({reason}). "
                      f"They remain at position 1.")

    def pay_fees(self, amount):
        if amount <= 0:
            print("Amount must be greater than zero.")
            return
        if self.total_fees == 0:
            print("No fees to pay.")
            return
        amount = min(amount, self.total_fees)
        self.paid += amount

        if self.db:
            self.db.execute(
                "UPDATE users SET paid = %s WHERE username = %s",
                (self.paid, self.username)
            )
            self.db.execute(
                "INSERT INTO payments (username, amount, paid_on) VALUES (%s, %s, %s)",
                (self.username, amount, datetime.now())
            )
        print(f"Paid P{amount:.2f}. Remaining fees: P{self.total_fees}")

    def view_dashboard(self):
        print(f"\n  {self.username}'s Dashboard  |  "
              f"Borrowing: {len(self.borrowed)}/{MAX_BORROW}  |  Fees: P{self.total_fees}")
        line()
        print(f"  {'ID':<4} {'Title':<25} {'Borrowed On':<12} {'Due':<12} {'Status':<10} Fee")
        line()
        for r in self.borrowed:
            flag = " !" if r.overdue_fee() else ""
            print(f"  {r.book_id:<4} {r.title[:24]:<25} "
                  f"{r.borrowed_on.strftime('%Y-%m-%d'):<12} "
                  f"{r.due_on.strftime('%Y-%m-%d'):<12} {'Borrowed':<10} "
                  f"P{r.overdue_fee()}{flag}")
        for r in self.history:
            print(f"  {r.book_id:<4} {r.title[:24]:<25} "
                  f"{r.borrowed_on.strftime('%Y-%m-%d'):<12} "
                  f"{r.due_on.strftime('%Y-%m-%d'):<12} {'Returned':<10} P{r.fee}")
            
        if self.waitlisted:
            line()
            print("  WAITLIST")
            print(f"  {'Book':<30} {'Position':<10}")
            line()
            for book in self.waitlisted:
                if self in book.waitlist:
                    pos = book.waitlist.index(self) + 1
                    print(f"  {book.title[:29]:<30} #{pos}")
        line()


class Admin(Person):
    def view_dashboard(self):
        print("Use view_report(library) for the full report.")

    def view_report(self, lib):
        users       = lib.users
        all_records = [r for u in users for r in u.borrowed + u.history]
        total_fees  = sum(u.total_fees for u in users)

        counts = {}
        for r in all_records:
            counts[r.title] = counts.get(r.title, 0) + 1
        top = max(counts, key=counts.get) if counts else "N/A"

        print("\n=== SYSTEM REPORT ===")
        print(f"  Users         : {len(users)}")
        print(f"  Active borrows: {sum(len(u.borrowed) for u in users)}")
        print(f"  Total returns : {sum(len(u.history) for u in users)}")
        print(f"  Fees owed     : P{total_fees}")
        print(f"  Most borrowed : {top}")
        line()
        if not all_records:
            print("  No borrow records yet.")
        else:
            print(f"  {'User':<12} {'ID':<4} {'Title':<25} "
                  f"{'Status':<10} {'Borrowed On':<12} {'Due/Returned':<12} Fee")
            line()
            for u in users:
                for r in u.borrowed:
                    flag = " !" if r.overdue_fee() else ""
                    print(f"  {u.username:<12} {r.book_id:<4} {r.title[:24]:<25} "
                          f"{'Borrowed':<10} {r.borrowed_on.strftime('%Y-%m-%d'):<12} "
                          f"{r.due_on.strftime('%Y-%m-%d'):<12} "
                          f"P{r.overdue_fee()}{flag}")
                for r in u.history:
                    print(f"  {u.username:<12} {r.book_id:<4} {r.title[:24]:<25} "
                          f"{'Returned':<10} {r.borrowed_on.strftime('%Y-%m-%d'):<12} "
                          f"{r.returned_on.strftime('%Y-%m-%d'):<12} P{r.fee}")
        line()


# LIBRARY — CENTRAL CONTROLLER
class Library:
    def __init__(self):
        self.books  = []
        self.users  = []
        self.admins = [Admin("admin", "123")]
        self.db = Database(DB_CONFIG)
        self._load_from_db()

    def _load_from_db(self):
        book_rows = self.db.fetchall("SELECT * FROM books ORDER BY id")
        if not book_rows:
            self._seed_default_books()
        else:
            for r in book_rows:
                book           = Book(r["title"], r["author"], r["dewey"],
                                      r["total"], r["year"], book_id=r["id"])
                book.available = r["available"]
                self.books.append(book)
            Book._next_id = max(b.id for b in self.books) + 1

        book_map = {b.id: b for b in self.books}

        user_rows = self.db.fetchall("SELECT * FROM users ORDER BY username")
        for r in user_rows:
            user        = User(r["username"], r["password_hash"],
                               db=self.db, pre_hashed=True)
            user.active = bool(r["active"])
            user.paid   = float(r["paid"])
            self.users.append(user)

        user_map = {u.username: u for u in self.users}

        rec_rows = self.db.fetchall("SELECT * FROM borrow_records ORDER BY id")
        for r in rec_rows:
            user = user_map.get(r["username"])
            if not user:
                continue
            book            = book_map.get(r["book_id"])
            rec             = BorrowRecord.__new__(BorrowRecord)
            rec.record_id   = r["id"]
            rec.book        = book
            rec.title       = r["book_title"]
            rec.book_id     = r["book_id"]
            rec.borrowed_on = r["borrowed_on"]
            rec.due_on      = r["due_on"]
            rec.returned_on = r["returned_on"]
            rec.fee         = float(r["fee"])

            if rec.returned_on is None:
                user.borrowed.append(rec)
            else:
                user.history.append(rec)

        wl_rows = self.db.fetchall(
            "SELECT * FROM waitlist ORDER BY book_id, position"
        )
        for r in wl_rows:
            book = book_map.get(r["book_id"])
            user = user_map.get(r["username"])
            if book and user and user not in book.waitlist:
                book.waitlist.append(user)
                if book not in user.waitlisted:      # keep user's side in sync
                    user.waitlisted.append(book)

        payment_rows = self.db.fetchall(
            "SELECT username, SUM(amount) as total_paid FROM payments GROUP BY username"
        )
        for r in payment_rows:
            user = user_map.get(r["username"])
            if user:
                user.paid = float(r["total_paid"])

    def _seed_default_books(self):
        defaults = [
            ("Intro to Programming",       "Ada Lovelace",          "500", 3, 2020),
            ("Philosophy 101",             "Aristotle",             "100", 2, None),
            ("World History",              "Howard Zinn",           "900", 4, 1980),
            ("Basic Science",              "Isaac Newton",          "500", 2, None),
            ("English Literature",         "Shakespeare",           "800", 5, None),
            ("Thinking, Fast and Slow",    "Daniel Kahneman",       "100", 5, 2011),
            ("A Brief History of Time",    "Stephen Hawking",       "500", 6, 1988),
            ("Sapiens",                    "Yuval Noah Harari",     "900", 8, 2011),
            ("The Pragmatic Programmer",   "Hunt & Thomas",         "000", 4, 1999),
            ("The Art of War",             "Sun Tzu",               "300", 7, 500),
            ("The Language Instinct",      "Steven Pinker",         "400", 3, 1994),
            ("The Story of Art",           "E.H. Gombrich",         "700", 5, 1950),
            ("The God Delusion",           "Richard Dawkins",       "200", 6, 2006),
            ("Don Quixote",                "Miguel de Cervantes",   "800", 4, 1605),
            ("The Republic",               "Plato",                 "100", 5, 380),
            ("Meditations",                "Marcus Aurelius",       "100", 6, 180),
            ("Nicomachean Ethics",         "Aristotle",             "100", 4, 350),
            ("Crime and Punishment",       "Fyodor Dostoevsky",     "800", 5, 1866),
            ("War and Peace",              "Leo Tolstoy",           "800", 6, 1869),
            ("1984",                       "George Orwell",         "800", 8, 1949),
            ("Brave New World",            "Aldous Huxley",         "800", 7, 1932),
            ("The Selfish Gene",           "Richard Dawkins",       "500", 6, 1976),
            ("Guns, Germs, and Steel",     "Jared Diamond",         "900", 7, 1997),
            ("The Origin of Species",      "Charles Darwin",        "500", 5, 1859),
            ("Cosmos",                     "Carl Sagan",            "500", 8, 1980),
            ("The Feynman Lectures",       "Richard Feynman",       "500", 4, 1963),
            ("Relativity",                 "Albert Einstein",       "500", 3, 1916),
            ("The Prince",                 "Niccolò Machiavelli",   "300", 5, 1532),
            ("The Wealth of Nations",      "Adam Smith",            "300", 4, 1776),
            ("The Communist Manifesto",    "Marx & Engels",         "300", 6, 1848),
            ("On Liberty",                 "John Stuart Mill",      "300", 4, 1859),
            ("Social Contract",            "Jean-Jacques Rousseau", "300", 3, 1762),
            ("Being and Time",             "Martin Heidegger",      "100", 2, 1927),
            ("Thus Spoke Zarathustra",     "Friedrich Nietzsche",   "100", 4, 1883),
            ("The Iliad",                  "Homer",                 "800", 5, 750),
            ("The Odyssey",                "Homer",                 "800", 6, 720),
            ("Hamlet",                     "William Shakespeare",   "800", 7, 1603),
            ("The Divine Comedy",          "Dante Alighieri",       "800", 5, 1320),
            ("Pride and Prejudice",        "Jane Austen",           "800", 8, 1813),
            ("Moby Dick",                  "Herman Melville",       "800", 4, 1851),
            ("The Great Gatsby",           "F. Scott Fitzgerald",   "800", 7, 1925),
            ("To Kill a Mockingbird",      "Harper Lee",            "800", 9, 1960),
            ("The Brothers Karamazov",     "Fyodor Dostoevsky",     "800", 5, 1880),
            ("Clean Code",                 "Robert C. Martin",      "600", 7, 2008),
            ("Design Patterns",            "Gang of Four",          "600", 4, 1994),
            ("The Mythical Man-Month",     "Fred Brooks",           "600", 5, 1975),
            ("Code Complete",              "Steve McConnell",       "600", 6, 1993),
            ("You Don't Know JS",          "Kyle Simpson",          "600", 5, 2014),
            ("Refactoring",                "Martin Fowler",         "600", 5, 1999),
            ("Thinking in Systems",        "Donella Meadows",       "000", 6, 2008),
            ("Gödel, Escher, Bach",        "Douglas Hofstadter",    "500", 5, 1979),
            ("The Art of Learning",        "Josh Waitzkin",         "100", 6, 2007),
            ("The Clean Coder",            "Robert C. Martin",      "600", 5, 2011)
        ]
        for t, a, d, c, y in defaults:
            cur = self.db.execute(
                "INSERT INTO books (title, author, dewey, total, available, year) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (t, a, d, c, c, y)
            )
            db_id = cur.lastrowid
            cur.close()
            book = Book(t, a, d, c, y, book_id=db_id)
            self.books.append(book)
        if self.books:
            Book._next_id = max(b.id for b in self.books) + 1

    def add_book(self, title, author, dewey, copies, year):
        cur = self.db.execute(
            "INSERT INTO books (title, author, dewey, total, available, year) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (title, author, dewey, copies, copies, year)
        )
        db_id = cur.lastrowid
        cur.close()
        book = Book(title, author, dewey, copies, year, book_id=db_id)
        self.books.append(book)
        print(f"Book '{title}' added!")

    def delete_book(self, book):
        self.db.execute("DELETE FROM waitlist WHERE book_id = %s", (book.id,))
        self.db.execute("DELETE FROM books     WHERE id      = %s", (book.id,))
        self.books.remove(book)
        print(f"Book '{book.title}' deleted.")

    def update_book(self, book):
        self.db.execute(
            "UPDATE books SET title=%s, author=%s, dewey=%s, "
            "total=%s, available=%s, year=%s WHERE id=%s",
            (book.title, book.author, book.dewey,
             book.total, book.available, book.year, book.id)
        )

    def find_by_id(self, book_id):
        return next((b for b in self.books if b.id == book_id), None)

    def find_by_title(self, title):
        return next((b for b in self.books if b.title.lower() == title.lower()), None)

    def find_by_id_or_title(self, query):
        if query.isdigit():
            return self.find_by_id(int(query))
        return self.find_by_title(query)

    def register(self, username, password):
        if len(username) < 3:
            print("Username must be at least 3 characters."); return None
        if any(u.username == username for u in self.users):
            print("Username already taken."); return None
        user = User(username, password, db=self.db)
        self.users.append(user)
        self.db.execute(
            "INSERT INTO users (username, password_hash, active, paid) "
            "VALUES (%s, %s, %s, %s)",
            (user.username, user._pw, 1, 0.00)
        )
        print(f"Registered '{username}'!"); return user

    def login_user(self, username, password):
        user = next((u for u in self.users if u.username == username), None)
        if user and user.check_password(password) and user.active:
            return user
        print("Invalid credentials or account inactive."); return None

    def login_admin(self, username, password):
        admin = next((a for a in self.admins if a.username == username), None)
        if admin and admin.check_password(password):
            return admin
        print("Access denied."); return None

    def show_books(self, query=""):
        results = [b for b in self.books
                   if query.lower() in b.title.lower()
                   or query.lower() in b.author.lower()
                   or query in b.dewey
                   or query.lower() in DEWEY_CATEGORIES.get(b.dewey, "").lower()]
        if not results:
            print("No books found."); return
        print(f"\n  {'ID':<4} {'Title':<25} {'Author':<18} {'Year':<6} {'Category':<20} Avail")
        line()
        for b in results:
            wl   = f" (waitlist:{len(b.waitlist)})" if b.waitlist else ""
            year = str(b.year) if b.year else "N/A"
            category = DEWEY_CATEGORIES.get(b.dewey, "General Knowledge")
            print(f"  {b.id:<4} {b.title[:24]:<25} {b.author[:17]:<18} "
                  f"{year:<6} {category:<20} {b.available}/{b.total}{wl}")
        line()


# CLI MENU FUNCTIONS
def admin_menu(admin, lib):
    dispatcher = EventDispatcher()

    def on_view_books():
        print("000: General Knowledge, 100: Philosophy,  200: Religion, "
              "\n300: Social Sciences,   400: Language,     500: Science, "
              "\n600: Technology,        700: Arts,         800: Literature, "
              "\n900: History")
        lib.show_books(input("Search (blank = all): ").strip())

    def on_add_book():
        title  = input("Title: ").strip()
        if not title: print("Title cannot be empty."); return
        author = input("Author: ").strip()
        if not author: print("Author cannot be empty."); return
        for code, cat in DEWEY_CATEGORIES.items():
            print(f"  {code}: {cat}")
        while True:
            dewey = input("Dewey code: ").strip()
            if dewey in DEWEY_CATEGORIES: break
            print(f"  Invalid code.")
        while True:
            copies = input("Copies: ").strip()
            if copies.isdigit() and int(copies) > 0: break
            print("  Enter a whole number > 0.")
        while True:
            year_input = input("Year published (blank to skip): ").strip()
            if not year_input: year = None; break
            if year_input.isdigit() and 1000 <= int(year_input) <= datetime.now().year:
                year = int(year_input); break
            print(f"  Invalid year.")
        lib.add_book(title, author, dewey, int(copies), year)

    def on_edit_book():
        lib.show_books()
        book = lib.find_by_id_or_title(input("ID or Title to edit: ").strip())
        if not book: print("Not found."); return
        book.title  = input(f"Title [{book.title}]: ").strip() or book.title
        book.author = input(f"Author [{book.author}]: ").strip() or book.author
        while True:
            nc = input(f"Copies [{book.total}]: ").strip()
            if not nc: break
            if nc.isdigit() and int(nc) > 0:
                new_total      = int(nc)
                currently_out  = book.total - book.available
                book.available = max(0, new_total - currently_out)
                book.total     = new_total; break
            print("  Invalid input.")
        while True:
            cur_year   = str(book.year) if book.year else ""
            year_input = input(f"Year [{cur_year or 'N/A'}]: ").strip()
            if not year_input: break
            if year_input.isdigit() and 1000 <= int(year_input) <= datetime.now().year:
                book.year = int(year_input); break
            print(f"  Invalid year.")
        print("Updated!")
        lib.update_book(book)

    def on_delete_book():
        lib.show_books()
        book = lib.find_by_id_or_title(input("ID or Title to delete: ").strip())
        if not book: print("Not found."); return
        if input(f"Delete '{book.title}'? (yes/no): ").strip().lower() == "yes":
            lib.delete_book(book)

    def on_report():
        admin.view_report(lib)
        input("\nPress Enter to continue...")

    def on_parallel_tasks():
        run_parallel_tasks(lib)

    dispatcher.register("view_books",     on_view_books)
    dispatcher.register("add_book",       on_add_book)
    dispatcher.register("edit_book",      on_edit_book)
    dispatcher.register("delete_book",    on_delete_book)
    dispatcher.register("report",         on_report)
    dispatcher.register("parallel_tasks", on_parallel_tasks)

    event_map = {
        "1": "view_books", "2": "add_book",   "3": "edit_book",
        "4": "delete_book","5": "report",      "6": "parallel_tasks",
    }

    while True:
        print("\n" + "=" * 35)
        print("         ADMIN PANEL")
        print("=" * 35)
        print("  1. View Books\n  2. Add Book\n  3. Edit Book")
        print("  4. Delete Book\n  5. Report\n  6. Parallel Report Generation")
        print("  7. Logout")
        print("=" * 35)
        c = input("> ").strip()
        if c == "7": break
        elif c in event_map: dispatcher.emit(event_map[c])
        else: print("Invalid option.")


def user_menu(user, lib):
    dispatcher = EventDispatcher()

    def on_view_books():
        print("000: General Knowledge, 100: Philosophy,  200: Religion, "
              "\n300: Social Sciences,   400: Language,     500: Science, "
              "\n600: Technology,        700: Arts,         800: Literature, "
              "\n900: History")
        lib.show_books(input("Search (blank = all): ").strip())

    def on_borrow():
        overdue = [r for r in user.borrowed if r.overdue_fee() > 0]
        if overdue:
            print(f"\n  Warning: You have {len(overdue)} overdue book(s). "
                  f"Total fees: P{user.total_fees}")
        print(f"\nRules: {BORROW_DAYS}-day loan | P{FEE_PER_DAY}/day overdue "
              f"| Max {MAX_BORROW} books\n")
        lib.show_books()
        bid = input("Book ID or Title to borrow (0 to cancel): ").strip()
        if bid and bid != "0":
            user.borrow_book(lib.find_by_id_or_title(bid))

    def on_return():
        if not user.borrowed: print("Nothing to return."); return
        user.view_dashboard()
        bid = input("Book ID to return (0 to cancel): ").strip()
        if bid.isdigit() and int(bid) != 0:
            user.return_book(int(bid))

    def on_pay_fees():
        if user.total_fees == 0: print("You have no outstanding fees."); return
        print(f"Outstanding fees: P{user.total_fees}")
        amt = input("Amount to pay P: ").strip()
        try:
            user.pay_fees(float(amt))
        except ValueError:
            print("Invalid amount.")

    def on_dashboard():
        user.view_dashboard()
        input("\nPress Enter to continue...")

    dispatcher.register("view_books",  on_view_books)
    dispatcher.register("borrow",      on_borrow)
    dispatcher.register("return_book", on_return)
    dispatcher.register("pay_fees",    on_pay_fees)
    dispatcher.register("dashboard",   on_dashboard)

    event_map = {
        "1": "view_books", "2": "borrow", "3": "return_book",
        "4": "pay_fees",   "5": "dashboard",
    }

    while True:
        print("\n" + "=" * 35)
        print(f"    USER MENU  [{user.username}]")
        print("=" * 35)
        print("  1. View Books\n  2. Borrow Book\n  3. Return Book")
        print("  4. Pay Fees\n  5. My Dashboard\n  7. Logout")
        print("=" * 35)
        c = input("> ").strip()
        if c == "7": break
        elif c in event_map: dispatcher.emit(event_map[c])
        else: print("Invalid option.")


def auth_menu(lib):
    dispatcher = EventDispatcher()
    result = [None]

    def on_login():
        user = lib.login_user(input("Username: ").strip(), input("Password: "))
        if user: result[0] = user

    def on_register():
        user = lib.register(input("Username: ").strip(), input("Password: "))
        if user: result[0] = user

    dispatcher.register("login",    on_login)
    dispatcher.register("register", on_register)
    event_map = {"1": "login", "2": "register"}

    while True:
        print("\n" + "=" * 35)
        print("           ACCOUNT")
        print("=" * 35)
        print("  1. Login\n  2. Register\n  3. Back")
        print("=" * 35)
        c = input("> ").strip()
        if c == "3": break
        elif c in event_map:
            dispatcher.emit(event_map[c])
            if result[0]: return result[0]
        else: print("Invalid option.")
    return None


def main():
    lib = Library()
    dispatcher = EventDispatcher()

    def on_admin():
        admin = lib.login_admin(
            input("Admin username: ").strip(), input("Password: ")
        )
        if admin: admin_menu(admin, lib)

    def on_user():
        user = auth_menu(lib)
        if user: user_menu(user, lib)

    dispatcher.register("admin", on_admin)
    dispatcher.register("user",  on_user)
    event_map = {"1": "admin", "2": "user"}

    while True:
        print("\n" + "=" * 35)
        print("   STACKED KNOWLEDGE")
        print("=" * 35)
        print("  1. Admin\n  2. User\n  3. Exit")
        print("=" * 35)
        c = input("> ").strip()
        if c == "3":
            print("Thank you for using Stacked Knowledge!")
            lib = None
            gc.collect()
            break
        elif c in event_map: dispatcher.emit(event_map[c])
        else: print("Invalid option.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()