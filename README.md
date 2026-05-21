# AI Chatbot Flask

An AI-powered chatbot web application built using Flask, SQLite, HTML, CSS, and Groq API.

## Features

- User Signup & Login
- Forgot Password with OTP
- AI Chatbot Responses
- Chat History
- Conversation Management
- SQLite Database
- Responsive UI

## Technologies Used

- Python
- Flask
- SQLite
- HTML/CSS/JavaScript
- Groq API
- Brevo Email API

## Project Structure

```bash
ai_chatbot/
│
├── app.py
├── chatbot.py
├── database.py
├── memory.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── chat.html
│   ├── forgot_password.html
│   ├── verify_otp.html
│   ├── reset_password.html
│   ├── terms.html
│   └── privacy.html
```

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/penchalajayanthi/ai-chatbot-flask.git
cd ai-chatbot-flask
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Create .env File

Create a `.env` file in project root.

```env
GROQ_API_KEY=your_groq_api_key
BREVO_API_KEY=your_brevo_api_key
```

### 4. Run Application

```bash
python app.py
```

## Open in Browser

```txt
http://127.0.0.1:5000
```

## Future Improvements

- Voice Assistant
- Dark Mode
- File Upload Chat
- AI Memory Improvements
- Deploy on Render

## Author

PenchalaJayanthi 