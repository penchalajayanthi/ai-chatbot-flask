from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import smtplib
import random
import requests
from chatbot import get_response
from itsdangerous import URLSafeTimedSerializer
from flask import url_for
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.secret_key = "secret"
s = URLSafeTimedSerializer(app.secret_key)


def send_email(to_email, otp):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    data = {
        "sender": {"email": "penchalajayanthi.balla@gmail.com"},
        "to": [{"email": to_email}],
        "subject": "Your OTP Code",
        "htmlContent": f"<h3>Your OTP is: {otp}</h3>"
    }

    response = requests.post(url, json=data, headers=headers)

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
def send_otp_email(to_email, otp):
    sender_email = "yourgmail@gmail.com"
    app_password = "your_app_password"

    msg = MIMEText(f"Your OTP for password reset is: {otp}")
    msg['Subject'] = "Password Reset OTP"
    msg['From'] = sender_email
    msg['To'] = to_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, app_password)
    server.send_message(msg)
    server.quit()

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    error_message = None

    if request.method == "POST":
        login_input = request.form.get("username")   # username or email
        pwd = request.form.get("password")

        if not login_input or not pwd:
            error_message = "Please enter username/email and password"
        else:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            
            c.execute("""
                SELECT * FROM users 
                WHERE (username = ? OR email = ?) 
            """, (login_input, login_input))
            
            user = c.fetchone()
            conn.close()

            if user is None:
                error_message = "User does not exist. Please sign up first."
            elif user[5] != pwd:     
                error_message = "Invalid username or password"
            else:
                # Login successful
                session["user"] = user[4] 
                return redirect("/chat")

    # Render login page with error message (if any)
    return render_template("login.html", error=error_message)



# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]

        # Create username from email (you can change this logic later)
        username = email.split('@')[0]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        try:
            c.execute("""
                INSERT INTO users (first_name, last_name, email, username, password)
                VALUES (?, ?, ?, ?, ?)
            """, (first_name, last_name, email, username, password))
            
            conn.commit()
            conn.close()

            return redirect("/")

        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists! Please use a different email."

    return render_template("signup.html")


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']   # ✅ ONLY EMAIL

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # ✅ FIXED QUERY (ONLY EMAIL)
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if not user:
            return render_template("forgot_password.html", error="Email not found")

        user_email = user[3]  # ✅ correct column

        print("Sending OTP to:", user_email)

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Save in session
        session['reset_email'] = user_email
        session['otp'] = otp

        # Send email
        send_email(user_email, otp)

        return redirect("/verify-otp")

    return render_template("forgot_password.html")

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']

        if user_otp == session.get('otp'):
            return redirect("/reset-password")
        else:
            return render_template("verify_otp.html", error="Invalid OTP")

    return render_template("verify_otp.html")

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # ✅ Validation
        if len(new_password) < 6:
            return render_template("reset_password.html", error="Password must be at least 6 characters")

        if new_password != confirm_password:
            return render_template("reset_password.html", error="Passwords do not match")

        email = session.get('reset_email')

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # ✅ Update password
        c.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
        conn.commit()
        conn.close()

        # Clear session
        session.pop('otp', None)
        session.pop('reset_email', None)

        return render_template("reset_password.html", message="Password updated successfully!")

    return render_template("reset_password.html")

@app.route("/chat")
def chat_page():
    if "user" not in session:
        return redirect("/")

    # ✅ RESET previous chat when page loads
    session.pop("convo_id", None)

    return render_template("chat.html", user=session["user"])
# NEW CHAT
@app.route("/new_chat")
def new_chat():
    user = session["user"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("INSERT INTO conversations (username, title) VALUES (?, ?)", (user, "New Chat"))
    convo_id = c.lastrowid

    conn.commit()
    conn.close()

    session["convo_id"] = convo_id

    return jsonify({"convo_id": convo_id})

@app.route("/rename_chat/<int:id>", methods=["POST"])
def rename_chat(id):
    data = request.get_json()
    new_title = data.get("title")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE conversations SET title=? WHERE id=?", (new_title, id))
    conn.commit()
    conn.close()

    return jsonify({"status": "renamed"})


# SEND MESSAGE
# @app.route("/chat", methods=["POST"])
# def chat_api():
#     # ✅ Check login
#     user = session.get("user")
#     if not user:
#         return jsonify({"error": "User not logged in"}), 401

#     # ✅ Get message
#     data = request.get_json()
#     msg = data.get("msg") if data else None

#     if not msg:
#         return jsonify({"error": "Empty message"}), 400

#     # ✅ Get conversation ID
#     convo_id = session.get("convo_id")

#     # ✅ DB connection
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()

#     # 🔥 If no chat exists → create one
#     if not convo_id:
#         c.execute(
#             "INSERT INTO conversations (username, title) VALUES (?, ?)",
#             (user, "New Chat")
#         )
#         convo_id = c.lastrowid
#         session["convo_id"] = convo_id

#     # ✅ Get bot reply
#     reply = get_response(user, msg)

#     # ✅ Save message
#     c.execute(
#         "INSERT INTO messages (convo_id, message, response) VALUES (?, ?, ?)",
#         (convo_id, msg, reply)
#     )

#     # 🔥 Dynamic title (only for first message)
#     c.execute("SELECT COUNT(*) FROM messages WHERE convo_id=?", (convo_id,))
#     count = c.fetchone()[0]

#     if count == 1:
#         title = msg[:25] + "..." if len(msg) > 25 else msg
#         c.execute(
#             "UPDATE conversations SET title=? WHERE id=?",
#             (title, convo_id)
#         )

#     conn.commit()
#     conn.close()

#     return jsonify({"reply": reply})
# SEND MESSAGE
@app.route("/chat", methods=["POST"])
def chat_api():
    user = session.get("user")
    if not user:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    msg = data.get("msg") if data else None

    if not msg:
        return jsonify({"error": "Empty message"}), 400

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # ✅ ALWAYS ensure convo exists
    convo_id = session.get("convo_id")

    if not convo_id:
        c.execute(
            "INSERT INTO conversations (username, title) VALUES (?, ?)",
            (user, "New Chat")
        )
        convo_id = c.lastrowid
        session["convo_id"] = convo_id

    # ✅ Get reply
    reply = get_response(user, msg)

    # ✅ Save message
    c.execute(
        "INSERT INTO messages (convo_id, message, response) VALUES (?, ?, ?)",
        (convo_id, msg, reply)
    )

    # ✅ Auto title (first message)
    c.execute("SELECT COUNT(*) FROM messages WHERE convo_id=?", (convo_id,))
    count = c.fetchone()[0]

    if count == 1:
        title = msg[:25] + "..." if len(msg) > 25 else msg
        c.execute("UPDATE conversations SET title=? WHERE id=?", (title, convo_id))

    conn.commit()
    conn.close()

    return jsonify({"reply": reply})

# GET CONVERSATIONS
# @app.route("/conversations")
# def conversations():
#     user = session["user"]

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT id,title FROM conversations WHERE username=?", (user,))
#     data = c.fetchall()
#     conn.close()

#     return jsonify({"convos": data})
@app.route("/conversations")
def conversations():
    user = session.get("user")

    if not user:
        return jsonify({"convos": []})

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT id,title FROM conversations WHERE username=?", (user,))
    data = c.fetchall()
    conn.close()

    return jsonify({"convos": data})

# LOAD CHAT
@app.route("/load_chat/<int:id>")
def load_chat(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT message, response FROM messages WHERE convo_id=?", (id,))
    chats = c.fetchall()
    conn.close()

    session["convo_id"] = id

    return jsonify({"chats": chats})


# DELETE CHAT
@app.route("/delete_chat/<int:id>")
def delete_chat(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("DELETE FROM messages WHERE convo_id=?", (id,))
    c.execute("DELETE FROM conversations WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"status": "deleted"})

# TERMS OF SERVICE
@app.route("/terms")
def terms():
    return render_template("terms.html")

# PRIVACY POLICY
@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)