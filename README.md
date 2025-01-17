SQL Chatbot
A natural language interface for SQL databases powered by Vanna AI. Interact with multiple SQL databases using plain English queries.

Features
Multi-database support:
SQLite (Demo database)
MySQL
SQL Server
PostgreSQL
Natural language to SQL conversion
Automatic visualization of query results
User-friendly interface
Prerequisites
Python 3.8 or higher
Required Python packages (install using requirements.txt)
Database drivers:
ODBC Driver 18 for SQL Server (for SQL Server connections)
PostgreSQL client libraries (for PostgreSQL connections)
MySQL Connector (for MySQL connections)
Installation
Clone the repository:
bash
Copy
Edit
git clone <repository-url>
cd <repository-folder>
Install the dependencies:
bash
Copy
Edit
pip install -r requirements.txt
Usage
Run the application:
bash
Copy
Edit
streamlit run app.py
Select your database type from the sidebar.
For the demo database, you can start asking questions immediately.
For other databases, enter your connection details:
Hostname
Port
Database name
Username
Password
Click Connect and start asking questions in natural language!
Example Queries
"Show me all customers and their total orders"
"What are the top 5 products by sales?"
"Show me monthly revenue trends"
Security
Database credentials are only used for the current session and are not stored.
All connections are made securely.
It's recommended to use a read-only database user for queries.
Steps to Fix on GitHub:
Ensure the above content is saved as README.md in your repository.
Push the updated file to GitHub:
bash
Copy
Edit
git add README.md
git commit -m "Fix README formatting"
git push origin main
Refresh your GitHub repository page to see the properly formatted README.
