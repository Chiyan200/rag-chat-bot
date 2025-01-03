# Flask API for Document Upload, User Management, and Chat System

This project is a Flask-based API application that handles document uploads, user management, chat functionalities, and integration with MongoDB for storing reports, documents, and chat history. The app allows users to register, login, upload PDFs, query documents, and interact with a bot via chat.

## Features

### User Management:
- User registration with validation for type, name, password, and email.
- Login functionality with email, password, and user type validation.

### Document Management:
- Upload PDF files and store them in a specific directory.
- Create and manage reports linked to uploaded PDFs.
- Fetch documents and reports by user email.

### Chat System:
- Users can create new chat rooms or interact with existing rooms.
- Bot integration for answering user queries related to documents.
- Chat history storage and retrieval for user queries.

## Requirements
- Python 3.9+
- Flask
- Flask-CORS
- PyMongo
- Python-dotenv
- MongoDB instance (for data storage)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Chiyan200/rag-chat-bot.git
cd rag-chat-bot
``` 

### 2. Install Dependencies
Create a virtual environment and install required dependencies:

## 1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv 
   ```

1. **Activate the virtual environment**:
   **On macOS/Linux**
   ```bash
   source venv/bin/activate
   ```

   **On On Windows**
   ```bash
   source venv\Scripts\activate
   ```
   **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 3. Set Up Environment Variables
Create a .env file in the root directory of the project and add the following environment variables:

```bash
MONGO_DB_URI=<your_mongo_db_uri>
DB_NAME=<your_database_name>
REPORT_COLLECTION=<your_report_collection>
USER_COLLECTION=<your_user_collection>
DOCUMENT_COLLECTION=<your_document_collection>
CHAT_COLLECTION=<your_chat_collection>
```
## 4. Run the Application
Run the Flask application using the following command:
```bash
python app.py
```