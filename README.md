🚀 SQL Chatbot Powered by LLM
An intelligent SQL Chatbot that transforms natural language questions into SQL queries and visualizes the results for efficient data analysis.

🔑 Features
Natural Language Querying: Easily generate SQL queries by typing simple questions.
Graphical Analysis: Get instant visual representations of query results.
PostgreSQL Support: Currently optimized for PostgreSQL (more databases coming soon!).
Secure & Private: No user data or credentials are collected.
🌐 Live Demo
🎯 How It Works
Connect Your Database: Use tools like ngrok to expose locally hosted databases.

Your exposed host should look like this:

Login with Credentials: Use your database credentials as shown below:


Ask Questions: Enter natural language questions, and the chatbot will generate SQL queries and visualize the results.

⚙️ Local Setup
Follow these steps to run the project locally:

Clone the repository:

bash
Copy
Edit
git clone https://github.com/Vitesh21/sql-chatbot
Install Dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Get a Vanna API Key:
Obtain a free API key from Vanna AI.

Update the API Key:
Replace the vanna_api_key variable in line 13 of app.py with your Vanna API key.

⚠️ Note: Do not push sensitive data to version control systems.

Run the App:

bash
Copy
Edit
streamlit run app.py
Deploy:
Deploy your app to Streamlit Cloud or your preferred platform.

📚 Technologies Used
Frontend: Streamlit
Backend: Python
Database: PostgreSQL
LLM Integration: Vanna AI
🔧 Future Improvements
Support for more database systems (MySQL, SQLite, etc.)
Enhanced query optimization
Improved visualizations and analytics
📜 License
This project is licensed under the MIT License.

