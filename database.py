import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# ====================== USERS TABLE ======================
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# ====================== CONVERSATIONS TABLE ======================
c.execute('''
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# ====================== MESSAGES TABLE ======================
c.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    convo_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (convo_id) REFERENCES conversations(id) ON DELETE CASCADE
)
''')

# ====================== COLLEGE INFO TABLE ======================
c.execute('''
CREATE TABLE IF NOT EXISTS college_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT UNIQUE NOT NULL,
    info TEXT NOT NULL
)
''')

# ====================== INSERT DEFAULT COLLEGE DATA ======================
college_data = [
    ("courses", "B.Tech (CSE, ECE, ME, Civil), B.Sc, BBA, MBA"),
    ("fees", "B.Tech: ₹1,20,000/year, MBA: ₹1,50,000/year"),
    ("placements", "90% placement rate. Highest: ₹12 LPA, Average: ₹4 LPA"),
    ("hostel", "Hostel available with WiFi, mess facility. Fee: ₹70,000/year"),
    ("admission", "Admissions are open. Apply online through merit or entrance exam."),
    ("location", "Hyderabad, Telangana, India"),
    ("contact", "Phone: +91 98765 43210 | Email: info@xyzcollege.edu.in"),
    ("website", "www.xyzcollege.edu.in")
]

# Clear previous college data and insert fresh
c.execute("DELETE FROM college_info")
c.executemany("INSERT INTO college_info (category, info) VALUES (?, ?)", college_data)

# ====================== INSERT DEFAULT ADMIN USER ======================
# Check if admin already exists to avoid duplicate error
c.execute("SELECT id FROM users WHERE username = ?", ("admin",))
if not c.fetchone():
    c.execute("""
        INSERT INTO users (first_name, last_name, email, username, password)
        VALUES (?, ?, ?, ?, ?)
    """, ("Admin", "User", "admin@xyzcollege.edu.in", "admin", "1234"))

# Optional: Drop old unused 'chats' table to clean up
c.execute("DROP TABLE IF EXISTS chats")

conn.commit()
conn.close()

print("✅ Database setup completed successfully!")
print("   • Users table with first_name, last_name, email")
print("   • Default admin created → username: admin | password: 1234")
print("   • College information loaded")
print("   • Old 'chats' table removed (if existed)")