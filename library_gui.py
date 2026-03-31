# =============================================================
# GUI MODULE — Stacked Knowledge: A Library System
# This file handles the graphical user interface (GUI) only.

# For the core logic and more comprehensive implementation of OOP principles, event-driven programming, parallel programming,
# memory management, and more, please refer to 'library.py'. 

# Similarly, Database interactions and queries are also handled in 'library.py'.
# Please refer to those file when grading the technical and database portion of the project.

# REQUIREMENTS:
# 1. 'library.py' must be in the same directory as this file.
# 2. XAMPP must be running with MySQL enabled before starting.
# =============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from library import Library, DEWEY_CATEGORIES


class lib_gui:
    def __init__(self, root):
        self.root = root
        self.root.title("Stacked Knowledge: A Library System")
        self.root.geometry("1000x750")

        self.COLOR_ROOT_BG = "#1c1c1c"
        self.COLOR_BG = "#f5f0e8"
        self.COLOR_PANEL = "#6b1626"
        self.COLOR_CARD = "#ffffff"
        self.COLOR_CARD_ALT = "#f0ebe0"
        self.COLOR_NAV = "#6b1626"
        self.COLOR_NAV_BORDER = "#8a1e30"
        self.COLOR_TEXT_DARK = "000000"
        self.COLOR_TEXT = "#f2ece0"
        self.COLOR_TEXT_MUTED = "#3a2a1a"
        self.COLOR_TEXT_SUBTLE = "#5a4535"
        self.COLOR_ACCENT = "#c9a84c"
        self.COLOR_ACCENT_DARK = "#9e7a28"
        self.COLOR_ACCENT_SOFT = "#3d3d3d"
        self.COLOR_SUCCESS = "#1a6e40"
        self.COLOR_WARNING = "#c9a84c"
        self.COLOR_ERROR = "#b03030"
        self.COLOR_INFO = "#4a6a8a"
        self.COLOR_STAT = "#6b1626"
        self.COLOR_LOGIN_BG = "#f5f0e8"
        self.COLOR_LOGIN_CARD = "#ffffff"
        self.COLOR_LOGIN_TEXT = "#1a1205"
        self.COLOR_LOGIN_MUTED = "#7a6248"
        self.COLOR_LOGIN_FIELD = "#f5f0e8"
        self.COLOR_LOGIN_LABEL = "#2a1a0a"
        self.COLOR_LOGIN_BTN = "#6b1626"
        self.COLOR_LOGIN_BTN2 = "#f0ebe0"
        self.COLOR_LOGIN_BTN2FG = "#2a1a0a"
        self.COLOR_REG_BTN = "#6b1626"
        self.COLOR_REG_BTNFG = "#f2ece0"
        self.COLOR_DIVIDER = "#c9a84c"

        self.root.configure(bg=self.COLOR_ROOT_BG)
        self.setup_styles()

        try:
            self.lib = Library()
        except Exception as e:
            messagebox.showerror("Database Error", f"Connection failed:\n{str(e)}\n\nMake sure MySQL is running!")
            self.root.destroy()
            return

        self.current_user = None
        self.current_admin = None
        self.show_login_screen()

    # ── STYLES ────────────────────────────────────────────────────────────────
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton',       font=('Segoe UI', 10), padding=8)
        style.configure('TLabel',        background=self.COLOR_CARD,    foreground=self.COLOR_TEXT,   font=('Segoe UI', 10))
        style.configure('TFrame',        background=self.COLOR_CARD)
        style.configure('TLabelframe',   background=self.COLOR_CARD,    foreground=self.COLOR_ACCENT)
        style.configure('TLabelframe.Label', background=self.COLOR_CARD, foreground=self.COLOR_ACCENT)
        style.configure('TEntry',        font=('Segoe UI', 10), padding=8)
        style.configure('TCombobox',     font=('Segoe UI', 10), padding=8)
        style.configure('Treeview', background=self.COLOR_CARD, foreground=self.COLOR_LOGIN_TEXT,
                        fieldbackground=self.COLOR_CARD, font=('Segoe UI', 9))
        style.configure('Treeview.Heading', background=self.COLOR_NAV, foreground=self.COLOR_TEXT,
                        font=('Segoe UI', 10, 'bold'), relief="flat")
        style.map('Treeview.Heading', background=[('active', self.COLOR_NAV)])

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def make_stat_cards(self, parent, cards):
        row = tk.Frame(parent, bg=self.COLOR_BG)
        row.pack(fill="x", pady=(0, 18))
        colors = [self.COLOR_STAT] * 4
        for i, (emoji, number, label, _) in enumerate(cards):
            color = colors[i % len(colors)]
            card = tk.Frame(row, bg=color, cursor="hand2")
            card.pack(side="left", expand=True, fill="both", padx=6, pady=4, ipadx=10, ipady=14)
            tk.Label(card, text=emoji, font=("Segoe UI", 26),
                     bg=color, fg=self.COLOR_TEXT).pack(side="left", padx=(14, 6))
            info = tk.Frame(card, bg=color)
            info.pack(side="left", expand=True)
            tk.Label(info, text=str(number), font=("Segoe UI", 22, "bold"),
                     bg=color, fg=self.COLOR_TEXT).pack(anchor="w")
            tk.Label(info, text=label, font=("Segoe UI", 10),
                     bg=color, fg=self.COLOR_TEXT).pack(anchor="w")

    def make_navbar(self, title, back_cmd=None, back_label="← Back", logout_cmd=None):
        nav = tk.Frame(self.root, bg=self.COLOR_NAV, height=56)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        tk.Label(nav, text=title, font=("Segoe UI", 13, "bold"),
                 bg=self.COLOR_NAV, fg=self.COLOR_TEXT).pack(side="left", padx=18, pady=14)
        if logout_cmd:
            tk.Button(nav, text="🚪 Logout", command=logout_cmd,
                      bg=self.COLOR_ERROR, fg=self.COLOR_TEXT,
                      activebackground=self.COLOR_ACCENT_DARK,
                      activeforeground=self.COLOR_TEXT,
                      font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                      padx=12, pady=6, cursor="hand2").pack(side="right", padx=10, pady=10)
        if back_cmd:
            tk.Button(nav, text=back_label, command=back_cmd,
                      bg=self.COLOR_CARD, fg=self.COLOR_NAV,
                      activebackground=self.COLOR_ACCENT_SOFT,
                      activeforeground=self.COLOR_TEXT,
                      font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                      padx=12, pady=6, cursor="hand2").pack(side="right", padx=4, pady=10)

    def make_action_buttons(self, parent, buttons):
        bar = tk.Frame(parent, bg=self.COLOR_BG)
        bar.pack(fill="x", pady=(0, 12))
        for label, cmd, bg, fg in buttons:
            tk.Button(bar, text=label, command=cmd,
                      bg=bg, fg=fg, font=("Segoe UI", 9, "bold"),
                      relief="flat", bd=0, padx=14, pady=8, cursor="hand2").pack(side="left", padx=4)
        return bar

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    def show_login_screen(self):
        self.clear_window()
        main = tk.Frame(self.root, bg=self.COLOR_ROOT_BG)
        main.pack(fill="both", expand=True)

        left = tk.Frame(main, bg=self.COLOR_PANEL, width=420)
        left.pack(side="left", fill="both")
        left.pack_propagate(False)

        tk.Frame(left, bg=self.COLOR_PANEL, height=80).pack()
        tk.Label(left, text="📚", font=("Segoe UI", 48),
                 bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).pack()
        tk.Label(left, text="Stacked Knowledge",
                 font=("Segoe UI", 22, "bold"),
                 bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).pack(pady=(10, 4))
        tk.Label(left, text="A Library System",
                 font=("Segoe UI", 11),
                 bg=self.COLOR_PANEL, fg="#f9fafb").pack()
        tk.Frame(left, bg=self.COLOR_DIVIDER, height=1).pack(fill="x", padx=40, pady=30)
        for emoji, text in [("📖", "Browse & borrow books"),
                             ("💳", "Track fees & payments"),
                             ("📊", "Admin analytics")]:
            row = tk.Frame(left, bg=self.COLOR_PANEL)
            row.pack(fill="x", padx=40, pady=5)
            tk.Label(row, text=emoji, font=("Segoe UI", 14),
                     bg=self.COLOR_PANEL, fg="#f9fafb").pack(side="left", padx=(0, 10))
            tk.Label(row, text=text, font=("Segoe UI", 10),
                     bg=self.COLOR_PANEL, fg="#f9fafb").pack(side="left")

        right = tk.Frame(main, bg=self.COLOR_LOGIN_BG)
        right.pack(side="right", fill="both", expand=True)

        card = tk.Frame(right, bg=self.COLOR_LOGIN_CARD, relief="flat")
        card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=460)

        tk.Label(card, text="Welcome Back 👋",
                 font=("Segoe UI", 18, "bold"),
                 bg=self.COLOR_LOGIN_CARD, fg=self.COLOR_LOGIN_TEXT).pack(pady=(36, 4))
        tk.Label(card, text="Sign in to your account",
                 font=("Segoe UI", 10),
                 bg=self.COLOR_LOGIN_CARD, fg=self.COLOR_LOGIN_MUTED).pack(pady=(0, 24))

        def field(parent, label_text, show=None):
            tk.Label(parent, text=label_text, font=("Segoe UI", 9, "bold"),
                     bg=self.COLOR_LOGIN_CARD, fg=self.COLOR_LOGIN_LABEL, anchor="w").pack(fill="x", padx=36, pady=(6, 2))
            e = tk.Entry(parent, font=("Segoe UI", 11), relief="solid", bd=1,
                         bg=self.COLOR_LOGIN_FIELD, fg=self.COLOR_LOGIN_TEXT, show=show or "")
            e.pack(fill="x", padx=36, ipady=8)
            return e

        username_entry = field(card, "Username")
        password_entry = field(card, "Password", show="•")

        tk.Label(card, text="Account Type", font=("Segoe UI", 9, "bold"),
                 bg=self.COLOR_LOGIN_CARD, fg=self.COLOR_LOGIN_LABEL, anchor="w").pack(fill="x", padx=36, pady=(10, 2))
        account_type = ttk.Combobox(card, values=["User", "Admin"], state="readonly", font=("Segoe UI", 11))
        account_type.set("User")
        account_type.pack(fill="x", padx=36)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get()
            acc_type = account_type.get()
            if not username or not password:
                messagebox.showerror("Error", "Please fill all fields"); return
            if acc_type == "Admin":
                admin = self.lib.login_admin(username, password)
                if admin:
                    self.current_admin = admin
                    self.show_admin_dashboard()
                else:
                    messagebox.showerror("Error", "Invalid admin credentials")
            else:
                user = self.lib.login_user(username, password)
                if user:
                    self.current_user = user
                    self.show_user_dashboard()
                else:
                    messagebox.showerror("Error", "Invalid user credentials")

        tk.Button(card, text="Sign In", command=login,
                  bg=self.COLOR_LOGIN_BTN, fg=self.COLOR_TEXT,
                  font=("Segoe UI", 11, "bold"),
                  relief="flat", bd=0, cursor="hand2").pack(fill="x", padx=36, pady=(22, 8), ipady=10)

        create_btn = tk.Button(card, text="Create Account",
                               command=self.show_register_screen,
                               bg=self.COLOR_LOGIN_BTN2, fg=self.COLOR_LOGIN_BTN2FG,
                               font=("Segoe UI", 10), relief="flat", bd=0, cursor="hand2")

        def toggle_create(event=None):
            if account_type.get() == "Admin":
                create_btn.pack_forget()
            else:
                create_btn.pack(fill="x", padx=36, ipady=6)

        create_btn.pack(fill="x", padx=36, ipady=6)
        account_type.bind("<<ComboboxSelected>>", toggle_create)

    # ── REGISTER ──────────────────────────────────────────────────────────────
    def show_register_screen(self):
        self.clear_window()
        main = tk.Frame(self.root, bg=self.COLOR_ROOT_BG)
        main.pack(fill="both", expand=True)

        left = tk.Frame(main, bg=self.COLOR_PANEL, width=420)
        left.pack(side="left", fill="both")
        left.pack_propagate(False)

        tk.Frame(left, bg=self.COLOR_PANEL, height=80).pack()
        tk.Label(left, text="📚", font=("Segoe UI", 48),
                 bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).pack()
        tk.Label(left, text="Stacked Knowledge",
                 font=("Segoe UI", 22, "bold"),
                 bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).pack(pady=(10, 4))
        tk.Label(left, text="A Library System",
                 font=("Segoe UI", 11),
                 bg=self.COLOR_PANEL, fg="#f9fafb").pack()
        tk.Frame(left, bg=self.COLOR_DIVIDER, height=1).pack(fill="x", padx=40, pady=30)
        for emoji, text in [("📖", "Browse & borrow books"),
                             ("💳", "Track fees & payments"),
                             ("📊", "Admin analytics")]:
            row = tk.Frame(left, bg=self.COLOR_PANEL)
            row.pack(fill="x", padx=40, pady=5)
            tk.Label(row, text=emoji, font=("Segoe UI", 14),
                     bg=self.COLOR_PANEL, fg="#f9fafb").pack(side="left", padx=(0, 10))
            tk.Label(row, text=text, font=("Segoe UI", 10),
                     bg=self.COLOR_PANEL, fg="#f9fafb").pack(side="left")

        right = tk.Frame(main, bg=self.COLOR_LOGIN_BG)
        right.pack(side="right", fill="both", expand=True)

        card = tk.Frame(right, bg=self.COLOR_LOGIN_CARD)
        card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=460)

        tk.Label(card, text="Create Account ✍️",
                 font=("Segoe UI", 18, "bold"),
                 bg=self.COLOR_LOGIN_CARD, fg=self.COLOR_LOGIN_TEXT).pack(pady=(36, 4))
        tk.Label(card, text="Register a new user account",
                 font=("Segoe UI", 10),
                 bg=self.COLOR_LOGIN_CARD, fg=self.COLOR_LOGIN_MUTED).pack(pady=(0, 24))

        def field(parent, label_text, show=None):
            tk.Label(parent, text=label_text, font=("Segoe UI", 9, "bold"),
                     bg=self.COLOR_LOGIN_CARD, fg=self.COLOR_LOGIN_LABEL, anchor="w").pack(fill="x", padx=36, pady=(6, 2))
            e = tk.Entry(parent, font=("Segoe UI", 11), relief="solid", bd=1,
                         bg=self.COLOR_LOGIN_FIELD, fg=self.COLOR_LOGIN_TEXT, show=show or "")
            e.pack(fill="x", padx=36, ipady=8)
            return e

        username_e = field(card, "Username")
        password_e = field(card, "Password", show="•")
        confirm_e  = field(card, "Confirm Password", show="•")

        def register():
            u, p, c = username_e.get().strip(), password_e.get(), confirm_e.get()
            if not u or not p:
                messagebox.showerror("Error", "Fill all fields"); return
            if p != c:
                messagebox.showerror("Error", "Passwords don't match"); return
            user = self.lib.register(u, p)
            if user:
                messagebox.showinfo("Success", f"Account '{u}' created!")
                self.current_user = user
                self.show_user_dashboard()
            else:
                messagebox.showerror("Error", "Registration failed")

        tk.Button(card, text="✓ Register", command=register,
                  bg=self.COLOR_REG_BTN, fg=self.COLOR_REG_BTNFG,
                  font=("Segoe UI", 11, "bold"),
                  relief="flat", bd=0, cursor="hand2").pack(fill="x", padx=36, pady=(22, 8), ipady=10)

        tk.Button(card, text="← Back to Login",
                  command=self.show_login_screen,
                  bg=self.COLOR_LOGIN_BTN2, fg=self.COLOR_LOGIN_BTN2FG,
                  font=("Segoe UI", 10), relief="flat", bd=0, cursor="hand2").pack(fill="x", padx=36, ipady=6)

    # ── USER DASHBOARD ────────────────────────────────────────────────────────
    def show_user_dashboard(self):
        self.clear_window()
        u = self.current_user

        self.make_navbar(f"📚  Library Dashboard  —  {u.username}", logout_cmd=self.logout)

        content = tk.Frame(self.root, bg=self.COLOR_BG)
        content.pack(fill="both", expand=True, padx=24, pady=20)

        borrowed_count = len(u.borrowed)
        overdue_count  = sum(1 for r in u.borrowed if r.overdue_fee() > 0)
        waitlist_count = len(u.waitlisted)

        self.make_stat_cards(content, [
            ("📖", borrowed_count,          "Books Borrowed", None),
            ("⚠️",  overdue_count,           "Overdue",        None),
            ("⏳", waitlist_count,           "On Waitlist",    None),
            ("💰", f"₱{u.total_fees:.0f}",  "Fees Due",       None),
        ])

        self.make_action_buttons(content, [
            ("📖  Browse Books",  self.show_user_books,    self.COLOR_ACCENT_SOFT, self.COLOR_TEXT),
            ("📋  My Borrowings", self.show_borrowings,    self.COLOR_ACCENT_DARK, self.COLOR_TEXT),
            ("⏳  My Waitlist",   self.show_user_waitlist, self.COLOR_INFO,        self.COLOR_TEXT),
            ("💳  Pay Fees",      self.show_pay_fees,      self.COLOR_WARNING,     "#000"),
        ])

        tk.Label(content, text="Current Borrowings",
                 font=("Segoe UI", 11, "bold"),
                 bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED).pack(anchor="w", pady=(6, 6))

        tree_frame = tk.Frame(content, bg=self.COLOR_BG)
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(tree_frame,
                            columns=("Title", "Due Date", "Status", "Fee"),
                            show="headings", height=10)
        for col, w in [("Title", 320), ("Due Date", 120), ("Status", 120), ("Fee", 80)]:
            tree.column(col, anchor="w" if col == "Title" else "center", width=w)
            tree.heading(col, text=col)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        tree.pack(fill="both", expand=True)

        tree.tag_configure("overdue",  background=self.COLOR_CARD, foreground=self.COLOR_ERROR)
        tree.tag_configure("active",   background=self.COLOR_CARD, foreground=self.COLOR_SUCCESS)
        tree.tag_configure("returned", background=self.COLOR_CARD, foreground=self.COLOR_TEXT_SUBTLE)

        for r in u.borrowed:
            status = "⚠️ Overdue" if r.overdue_fee() > 0 else "✓ Active"
            tag    = "overdue"   if r.overdue_fee() > 0 else "active"
            tree.insert("", "end",
                        values=(r.title[:45], r.due_on.strftime("%Y-%m-%d"),
                                status, f"₱{r.overdue_fee():.2f}"),
                        tags=(tag,))

        for r in u.history:
            tree.insert("", "end",
                        values=(r.title[:45],
                                r.returned_on.strftime("%Y-%m-%d") if r.returned_on else "—",
                                "✓ Returned", f"₱{r.fee:.2f}"),
                        tags=("returned",))

    # ── USER → VIEW BOOKS ─────────────────────────────────────────────────────
    def show_user_books(self):
        self.clear_window()
        self.make_navbar("📖  Available Books", back_cmd=self.show_user_dashboard)

        content = tk.Frame(self.root, bg=self.COLOR_BG)
        content.pack(fill="both", expand=True, padx=20, pady=16)

        sf = tk.Frame(content, bg=self.COLOR_CARD)
        sf.pack(fill="x", pady=(0, 12))

        tk.Label(sf, text="🔍", font=("Segoe UI", 12),
                 bg=self.COLOR_CARD, fg=self.COLOR_ACCENT).pack(side="left", padx=10, pady=10)
        search_e = tk.Entry(sf, font=("Segoe UI", 11), relief="flat", bd=0,
                            bg=self.COLOR_CARD, fg=self.COLOR_LOGIN_TEXT,
                            insertbackground=self.COLOR_LOGIN_TEXT)
        search_e.pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(sf, text="Search", command=lambda: display(search_e.get()),
                  bg=self.COLOR_ACCENT_SOFT, fg=self.COLOR_TEXT,
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", bd=0, padx=14, pady=8, cursor="hand2").pack(side="right", padx=6, pady=6)

        tk.Label(content,
                 text="Search by title, author, category name or Dewey code"
                      "\n(000: General Knowledge, 100: Philosophy, 200: Religion, 300: Social Sciences, "
                      "400: Language, 500: Science, 600: Technology, 700: Arts, 800: Literature, 900: History)",
                 font=("Segoe UI", 8), bg=self.COLOR_BG,
                 fg=self.COLOR_TEXT_SUBTLE, justify="left").pack(anchor="w", pady=(2, 6))

        tf = tk.Frame(content, bg=self.COLOR_BG)
        tf.pack(fill="both", expand=True)

        tree = ttk.Treeview(tf,
                            columns=("ID", "Title", "Author", "Category", "Available", "Waitlist"),
                            show="headings", height=16)
        for col, w, anchor in [("ID", 45, "center"), ("Title", 240, "w"),
                               ("Author", 140, "w"), ("Category", 130, "w"),
                               ("Available", 90, "center"), ("Waitlist", 80, "center")]:
            tree.column(col, width=w, anchor=anchor)
            tree.heading(col, text=col)

        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        tree.pack(fill="both", expand=True)

        tree.tag_configure("avail",    background=self.COLOR_CARD, foreground=self.COLOR_SUCCESS)
        tree.tag_configure("unavail",  background=self.COLOR_CARD, foreground=self.COLOR_ERROR)
        tree.tag_configure("waitlist", background=self.COLOR_CARD, foreground=self.COLOR_INFO)

        def display(q=""):
            for i in tree.get_children(): tree.delete(i)
            for b in self.lib.books:
                category = DEWEY_CATEGORIES.get(b.dewey, "General Knowledge")
                if (q.lower() in b.title.lower() or
                        q.lower() in b.author.lower() or
                        q == b.dewey or
                        q.lower() in category.lower()):
                    wl_count = len(b.waitlist)
                    if b.available > 0:
                        tag = "avail"
                    elif wl_count > 0:
                        tag = "waitlist"
                    else:
                        tag = "unavail"
                    tree.insert("", "end",
                                values=(b.id, b.title[:40], b.author[:28],
                                        category, f"{b.available}/{b.total}",
                                        wl_count if wl_count > 0 else "—"),
                                tags=(tag,))
        display()

        def borrow_or_waitlist():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a book first"); return
            bid  = tree.item(sel[0])["values"][0]
            book = self.lib.find_by_id(bid)
            u    = self.current_user

            if len(u.borrowed) >= 5:
                messagebox.showerror("Error", "Borrow limit reached (5 books max)")
                return
            if u.total_fees > 0:
                messagebox.showerror("Error", f"Settle your fees first: ₱{u.total_fees:.2f}")
                return

            if book.available > 0:
                # Normal borrow
                u.borrow_book(book)
                messagebox.showinfo("Success", f"✅ Borrowed '{book.title}'!")
                self.show_user_dashboard()
            else:
                if u in book.waitlist:
                    pos = book.waitlist.index(u) + 1
                    messagebox.showinfo(
                        "Already on Waitlist",
                        f"You're already on the waitlist for '{book.title}'.\n"
                        f"Your position: #{pos}"
                    )
                    return
                answer = messagebox.askyesno(
                    "Book Unavailable",
                    f"'{book.title}' is currently out of copies.\n\n"
                    f"There are {len(book.waitlist)} user(s) already waiting.\n\n"
                    f"Would you like to join the waitlist?"
                )
                if answer:
                    u._join_waitlist(book)
                    pos = book.waitlist.index(u) + 1
                    messagebox.showinfo(
                        "✅ Added to Waitlist",
                        f"You've been added to the waitlist for '{book.title}'.\n"
                        f"Your position: #{pos}\n\n"
                        f"You'll be automatically borrowed the book when it becomes available."
                    )
                    display()  # refresh to show updated waitlist count

        self.make_action_buttons(content, [
            ("📤  Borrow / Join Waitlist", borrow_or_waitlist, self.COLOR_SUCCESS, "#000"),
        ])

    def show_user_waitlist(self):
        self.clear_window()
        self.make_navbar("⏳  My Waitlist", back_cmd=self.show_user_dashboard)

        content = tk.Frame(self.root, bg=self.COLOR_BG)
        content.pack(fill="both", expand=True, padx=20, pady=16)

        u = self.current_user

        if not u.waitlisted:
            tk.Label(content,
                     text="You are not on any waitlists.",
                     font=("Segoe UI", 12),
                     bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED).pack(pady=40)
            return

        tk.Label(content,
                 text="When a book becomes available, it will be automatically borrowed for you\n"
                      "(as long as you're under the 5-book limit and have no outstanding fees).",
                 font=("Segoe UI", 9),
                 bg=self.COLOR_BG, fg=self.COLOR_TEXT_SUBTLE,
                 justify="left").pack(anchor="w", pady=(0, 10))

        tf = tk.Frame(content, bg=self.COLOR_BG)
        tf.pack(fill="both", expand=True)

        tree = ttk.Treeview(tf,
                            columns=("Title", "Author", "Category", "Position", "Queue Size"),
                            show="headings", height=20)
        for col, w, anchor in [("Title", 280, "w"), ("Author", 160, "w"),
                                ("Category", 130, "w"),
                                ("Position", 90, "center"), ("Queue Size", 100, "center")]:
            tree.column(col, width=w, anchor=anchor)
            tree.heading(col, text=col)

        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        tree.pack(fill="both", expand=True)

        tree.tag_configure("first",  background=self.COLOR_CARD, foreground=self.COLOR_SUCCESS)
        tree.tag_configure("waiting", background=self.COLOR_CARD, foreground=self.COLOR_INFO)

        for book in u.waitlisted:
            if u in book.waitlist:
                pos      = book.waitlist.index(u) + 1
                category = DEWEY_CATEGORIES.get(book.dewey, "General Knowledge")
                tag      = "first" if pos == 1 else "waiting"
                tree.insert("", "end",
                            values=(book.title[:45], book.author[:28],
                                    category, f"#{pos}", len(book.waitlist)),
                            tags=(tag,))

        # Leave waitlist button
        def leave_waitlist():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a book first"); return

            title = tree.item(sel[0])["values"][0]
            book  = next((b for b in self.lib.books if b.title.startswith(title.rstrip("."))), None)
            if not book:
                return

            answer = messagebox.askyesno(
                "Leave Waitlist",
                f"Remove yourself from the waitlist for\n'{book.title}'?"
            )
            if not answer:
                return

            if u in book.waitlist:
                book.waitlist.remove(u)
            if book in u.waitlisted:
                u.waitlisted.remove(book)

            # Clean up DB and renumber
            if self.lib.db:
                self.lib.db.execute(
                    "DELETE FROM waitlist WHERE book_id = %s AND username = %s",
                    (book.id, u.username)
                )
                for pos, waiting_user in enumerate(book.waitlist):
                    self.lib.db.execute(
                        "INSERT INTO waitlist (book_id, username, position) "
                        "VALUES (%s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE position = VALUES(position)",
                        (book.id, waiting_user.username, pos)
                    )

            messagebox.showinfo("✅ Removed", f"You've been removed from the waitlist for '{book.title}'.")
            self.show_user_waitlist()

        self.make_action_buttons(content, [
            ("❌  Leave Waitlist", leave_waitlist, self.COLOR_ERROR, self.COLOR_TEXT),
        ])

    # ── USER → MY BORROWINGS ──────────────────────────────────────────────────
    def show_borrowings(self):
        self.clear_window()
        self.make_navbar("📋  My Borrowings", back_cmd=self.show_user_dashboard)

        content = tk.Frame(self.root, bg=self.COLOR_BG)
        content.pack(fill="both", expand=True, padx=20, pady=16)

        tf = tk.Frame(content, bg=self.COLOR_BG)
        tf.pack(fill="both", expand=True)

        tree = ttk.Treeview(tf,
                            columns=("ID", "Title", "Due Date", "Status", "Fee"),
                            show="headings", height=20)
        for col, w, anchor in [("ID", 45, "center"), ("Title", 300, "w"),
                                ("Due Date", 110, "center"), ("Status", 110, "center"),
                                ("Fee", 80, "center")]:
            tree.column(col, width=w, anchor=anchor)
            tree.heading(col, text=col)

        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        tree.pack(fill="both", expand=True)

        tree.tag_configure("overdue",  background=self.COLOR_CARD, foreground=self.COLOR_ERROR)
        tree.tag_configure("active",   background=self.COLOR_CARD, foreground=self.COLOR_SUCCESS)
        tree.tag_configure("returned", background=self.COLOR_CARD, foreground=self.COLOR_TEXT_SUBTLE)

        for r in self.current_user.borrowed:
            status = "⚠️ Overdue" if r.overdue_fee() > 0 else "✓ Active"
            tag    = "overdue"   if r.overdue_fee() > 0 else "active"
            tree.insert("", "end",
                        values=(r.book_id, r.title[:38], r.due_on.strftime("%Y-%m-%d"),
                                status, f"₱{r.overdue_fee():.2f}"),
                        tags=(tag,))

        for r in self.current_user.history:
            tree.insert("", "end",
                        values=(r.book_id, r.title[:38],
                                r.returned_on.strftime("%Y-%m-%d") if r.returned_on else "—",
                                "✓ Returned", f"₱{r.fee:.2f}"),
                        tags=("returned",))

        def return_book():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a book first"); return
            bid = tree.item(sel[0])["values"][0]
            self.current_user.return_book(bid)
            messagebox.showinfo("Success", "✅ Book returned!")
            self.show_borrowings()

        self.make_action_buttons(content, [
            ("📥  Return Selected", return_book, self.COLOR_WARNING, "#000"),
        ])

    # ── USER → PAY FEES ───────────────────────────────────────────────────────
    def show_pay_fees(self):
        if self.current_user.total_fees == 0:
            messagebox.showinfo("✓ No Fees", "You have no outstanding fees!"); return

        top = tk.Toplevel(self.root)
        top.title("💳 Pay Fees")
        top.geometry("340x230")
        top.configure(bg=self.COLOR_CARD)
        top.resizable(False, False)
        top.transient(self.root)
        top.grab_set()

        c = tk.Frame(top, bg=self.COLOR_CARD)
        c.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(c, text="Outstanding Fees", font=("Segoe UI", 14, "bold"),
                 bg=self.COLOR_CARD, fg=self.COLOR_ACCENT).pack(pady=(0, 8))
        tk.Label(c, text=f"₱{self.current_user.total_fees:.2f}",
                 font=("Segoe UI", 28, "bold"),
                 bg=self.COLOR_CARD, fg=self.COLOR_ERROR).pack()

        tk.Label(c, text="Amount to Pay (₱):", font=("Segoe UI", 9),
                 bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED).pack(anchor="w", pady=(18, 4))
        amt_e = tk.Entry(c, font=("Segoe UI", 12), relief="flat", bd=0,
                         bg=self.COLOR_CARD_ALT, fg=self.COLOR_TEXT,
                         insertbackground=self.COLOR_TEXT)
        amt_e.pack(fill="x", ipady=8)

        def pay():
            try:
                amount = float(amt_e.get())
                if amount <= 0: raise ValueError
                if amount > self.current_user.total_fees:
                    messagebox.showwarning("Warning", f"You only owe ₱{self.current_user.total_fees:.2f}"); return
                self.current_user.pay_fees(amount)
                messagebox.showinfo("✓ Success", f"Payment of ₱{amount:.2f} processed!")
                top.destroy()
                self.show_user_dashboard()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")

        tk.Button(c, text="💳  Process Payment", command=pay,
                  bg=self.COLOR_SUCCESS, fg="#000", font=("Segoe UI", 11, "bold"),
                  relief="flat", bd=0, cursor="hand2").pack(fill="x", pady=16, ipady=10)

    # ── ADMIN DASHBOARD ───────────────────────────────────────────────────────
    def show_admin_dashboard(self):
        self.clear_window()
        self.make_navbar("🔐  Admin Dashboard", logout_cmd=self.logout)

        content = tk.Frame(self.root, bg=self.COLOR_BG)
        content.pack(fill="both", expand=True, padx=24, pady=20)

        total_users    = len(self.lib.users)
        active_borrows = sum(len(u.borrowed) for u in self.lib.users)
        total_books    = len(self.lib.books)
        total_fees     = sum(u.total_fees for u in self.lib.users)

        self.make_stat_cards(content, [
            ("👥", total_users,          "Total Users",    None),
            ("📖", active_borrows,       "Active Borrows", None),
            ("📚", total_books,          "Total Books",    None),
            ("💰", f"₱{total_fees:.0f}", "Fees Owed",      None),
        ])

        self.make_action_buttons(content, [
            ("📚  Manage Books", self.show_admin_books,  self.COLOR_ACCENT_SOFT, self.COLOR_TEXT),
            ("📊  User Report",  self.show_admin_report, self.COLOR_ACCENT_DARK, self.COLOR_TEXT),
            ("💰  Fee Overview", self.show_user_fees,    self.COLOR_WARNING,     "#000"),
        ])

        tk.Label(content, text="Users — Active Borrowings",
                 font=("Segoe UI", 11, "bold"),
                 bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED).pack(anchor="w", pady=(6, 6))

        tf = tk.Frame(content, bg=self.COLOR_BG)
        tf.pack(fill="both", expand=True)

        tree = ttk.Treeview(tf,
                            columns=("User", "Borrowed", "Overdue", "Waitlisted", "Fees"),
                            show="headings", height=10)
        for col, w, anchor in [("User", 200, "w"), ("Borrowed", 100, "center"),
                                ("Overdue", 100, "center"), ("Waitlisted", 100, "center"),
                                ("Fees", 120, "center")]:
            tree.column(col, width=w, anchor=anchor)
            tree.heading(col, text=col)

        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        tree.pack(fill="both", expand=True)

        tree.tag_configure("warn",   background=self.COLOR_CARD, foreground=self.COLOR_ERROR)
        tree.tag_configure("normal", background=self.COLOR_CARD, foreground=self.COLOR_SUCCESS)

        for u in self.lib.users:
            overdue    = sum(1 for r in u.borrowed if r.overdue_fee() > 0)
            waitlisted = len(u.waitlisted)
            tag = "warn" if u.total_fees > 0 else "normal"
            tree.insert("", "end",
                        values=(u.username, len(u.borrowed), overdue,
                                waitlisted, f"₱{u.total_fees:.2f}"),
                        tags=(tag,))

    # ── ADMIN → MANAGE BOOKS ──────────────────────────────────────────────────
    def show_admin_books(self):
        self.clear_window()
        self.make_navbar("📚  Manage Books", back_cmd=self.show_admin_dashboard)

        content = tk.Frame(self.root, bg=self.COLOR_BG)
        content.pack(fill="both", expand=True, padx=20, pady=16)

        tf = tk.Frame(content, bg=self.COLOR_BG)
        tf.pack(fill="both", expand=True, pady=(0, 12))

        tree = ttk.Treeview(tf,
                            columns=("ID", "Title", "Author", "Category", "Total", "Available", "Waitlist"),
                            show="headings", height=18)
        for col, w, anchor in [("ID", 45, "center"), ("Title", 230, "w"),
                               ("Author", 130, "w"), ("Category", 110, "w"),
                               ("Total", 55, "center"), ("Available", 75, "center"),
                               ("Waitlist", 70, "center")]:
            tree.column(col, width=w, anchor=anchor)
            tree.heading(col, text=col)

        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        tree.pack(fill="both", expand=True)

        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for b in self.lib.books:
                category = DEWEY_CATEGORIES.get(b.dewey, "General Knowledge")
                tree.insert("", "end",
                            values=(b.id, b.title[:38], b.author[:26],
                                    category, b.total, b.available,
                                    len(b.waitlist) if b.waitlist else "—"))
        refresh()

        def add_book():
            win = tk.Toplevel(self.root)
            win.title("➕ Add Book")
            win.geometry("420x320")
            win.configure(bg=self.COLOR_CARD)
            win.resizable(False, False)
            win.transient(self.root)
            win.grab_set()

            c = tk.Frame(win, bg=self.COLOR_CARD)
            c.pack(fill="both", expand=True, padx=24, pady=16)

            tk.Label(c, text="Add New Book", font=("Segoe UI", 14, "bold"),
                     bg=self.COLOR_CARD, fg=self.COLOR_ACCENT).pack(pady=(0, 12))

            entries = {}
            for lbl in ["Title", "Author", "Dewey Code", "Copies"]:
                tk.Label(c, text=lbl, font=("Segoe UI", 9),
                         bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED, anchor="w").pack(fill="x", pady=(6, 2))
                e = tk.Entry(c, font=("Segoe UI", 11), relief="flat", bd=0,
                             bg=self.COLOR_CARD_ALT, fg=self.COLOR_LOGIN_TEXT,
                             insertbackground=self.COLOR_TEXT)
                e.pack(fill="x", ipady=7)
                tk.Frame(c, bg=self.COLOR_DIVIDER, height=1).pack(fill="x")
                entries[lbl] = e

            def save():
                title  = entries["Title"].get().strip()
                author = entries["Author"].get().strip()
                dewey  = entries["Dewey Code"].get().strip() or "000"
                try:
                    copies = int(entries["Copies"].get())
                    self.lib.add_book(title, author, dewey, copies, 2024)
                    refresh()
                    win.destroy()
                    messagebox.showinfo("✓ Success", "Book added!")
                except ValueError:
                    messagebox.showerror("Error", "Invalid copies value")

            tk.Button(c, text="✓  Save Book", command=save,
                      bg=self.COLOR_SUCCESS, fg="#000", font=("Segoe UI", 11, "bold"),
                      relief="flat", bd=0, cursor="hand2").pack(fill="x", pady=18, ipady=10)

        def delete_book():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a book first"); return
            bid  = tree.item(sel[0])["values"][0]
            book = self.lib.find_by_id(bid)
            if messagebox.askyesno("Confirm", f"Delete '{book.title}'?"):
                self.lib.delete_book(book)
                refresh()
                messagebox.showinfo("✓ Success", "Book deleted!")

        self.make_action_buttons(content, [
            ("➕  Add Book",    add_book,    self.COLOR_SUCCESS, "#000"),
            ("🗑️  Delete Book", delete_book, self.COLOR_ERROR,   self.COLOR_TEXT),
        ])

    # ── ADMIN → REPORT ────────────────────────────────────────────────────────
    def show_admin_report(self):
        self.clear_window()
        self.make_navbar("📊  User Report", back_cmd=self.show_admin_dashboard)

        content = tk.Frame(self.root, bg=self.COLOR_BG)
        content.pack(fill="both", expand=True, padx=20, pady=16)

        tf = tk.Frame(content, bg=self.COLOR_BG)
        tf.pack(fill="both", expand=True)

        tree = ttk.Treeview(tf,
                            columns=("User", "Borrowed", "Overdue", "Waitlisted", "Fees"),
                            show="headings", height=22)
        for col, w, anchor in [("User", 220, "w"), ("Borrowed", 120, "center"),
                                ("Overdue", 120, "center"), ("Waitlisted", 120, "center"),
                                ("Fees", 120, "center")]:
            tree.column(col, width=w, anchor=anchor)
            tree.heading(col, text=col)

        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        tree.pack(fill="both", expand=True)

        tree.tag_configure("warn",   background=self.COLOR_CARD, foreground=self.COLOR_ERROR)
        tree.tag_configure("normal", background=self.COLOR_CARD, foreground=self.COLOR_SUCCESS)

        for u in self.lib.users:
            overdue    = sum(1 for r in u.borrowed if r.overdue_fee() > 0)
            waitlisted = len(u.waitlisted)
            tag = "warn" if u.total_fees > 0 else "normal"
            tree.insert("", "end",
                        values=(u.username, len(u.borrowed), overdue,
                                waitlisted, f"₱{u.total_fees:.2f}"),
                        tags=(tag,))

    # ── ADMIN → FEE OVERVIEW ──────────────────────────────────────────────────
    def show_user_fees(self):
        self.clear_window()
        self.make_navbar("💰  Fee Overview", back_cmd=self.show_admin_dashboard)

        content = tk.Frame(self.root, bg=self.COLOR_BG)
        content.pack(fill="both", expand=True, padx=20, pady=16)

        tf = tk.Frame(content, bg=self.COLOR_BG)
        tf.pack(fill="both", expand=True)

        tree = ttk.Treeview(tf,
                            columns=("User", "Total Owed", "Paid", "Remaining"),
                            show="headings", height=22)
        for col, w in [("User", 220), ("Total Owed", 160), ("Paid", 160), ("Remaining", 160)]:
            tree.column(col, width=w, anchor="center" if col != "User" else "w")
            tree.heading(col, text=col)

        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        tree.pack(fill="both", expand=True)

        tree.tag_configure("unpaid", background=self.COLOR_CARD, foreground=self.COLOR_ERROR)
        tree.tag_configure("paid",   background=self.COLOR_CARD, foreground=self.COLOR_SUCCESS)

        for u in self.lib.users:
            total_owed = sum(r.overdue_fee() for r in u.borrowed) + sum(r.fee for r in u.history)
            remaining  = u.total_fees
            tag = "unpaid" if remaining > 0 else "paid"
            tree.insert("", "end",
                        values=(u.username, f"₱{total_owed:.2f}", f"₱{u.paid:.2f}", f"₱{remaining:.2f}"),
                        tags=(tag,))

    # ── UTILS ─────────────────────────────────────────────────────────────────
    def logout(self):
        self.current_user  = None
        self.current_admin = None
        self.show_login_screen()

    def clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = lib_gui(root)
    root.mainloop()