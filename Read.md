🏆 Ultimate Cup Website

The Ultimate Cup website is a dynamic football tournament management platform built to streamline match fixtures, display team standings, and showcase player performance in real time. It provides an engaging and user-friendly interface for administrators, teams, and fans to interact seamlessly.

🚀 Features
🔹 For Users

View match fixtures, results, and live updates.

Check team standings, goal scorers, and tournament statistics.

Responsive and mobile-friendly interface for smooth browsing.

🔹 For Admins

Secure admin dashboard to manage teams, fixtures, and scores.

Add or update match fixtures, results, and goal scorers.

Intuitive data entry forms with clean and modern UI design.

🧰 Tech Stack
Category	Technology
Frontend	HTML, CSS, JavaScript, Bootstrap
Backend	Flask (Python)
Database	SQLite / MySQL
Hosting	 Render, & GitHub Pages for static parts
Version Control	Git & GitHub

⚙️ Installation & Setup

Follow these steps to run the project locally:

1️⃣ Clone the Repository
git clone https://github.com/your-username/ultimate-cup.git
cd ultimate-cup

2️⃣ Create a Virtual Environment
python -m venv venv
source venv/bin/activate    # For Mac/Linux
venv\Scripts\activate       # For Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Flask App
python app.py

5️⃣ Open in Browser

Visit http://127.0.0.1:5000

🖼️ Screenshots (Optional)
Homepage	Admin Dashboard	Fixtures Page

	
	
💡 Project Structure  
ultimate-cup/  
│  
├── static/  
│   ├── css/  
│   ├── js/  
│   └── images/  
│  
├── templates/  
│   ├── index.html  
│   ├── fixtures.html  
│   ├── admin_dashboard.html  
│   └── ...  
│  
├── app.py  
├── models.py  
├── requirements.txt  
└── README.md  
  
🧩 Key Functionalities  

⚔️ Add Match Fixture: Admins can add new matches, including date, time, and venue.  

🥅 Update Scores: Input match results and automatically update tables.  

👟 Goal Scorers Display: Player names appear in italic and slightly smaller than team names for better readability.  

📊 Tournament Statistics: Dynamic tables showing team performance, points, and ranking.  

🌐 Deployment  

You can deploy the project using:  

Render (recommended for Flask apps)  

Railway  

PythonAnywhere  

Vercel (via adapter)  

Add environment variables such as:  

FLASK_ENV=production  
SECRET_KEY=your_secret_key  
DATABASE_URL=your_database_url  

👨‍💻 Author  

Gabriel Simeon  
💼 Data Analyst | Developer | Tech Educator  
📧 gabrielsimeon443@gmail.com
]  
🌍 LinkedIn Profile: https://www.linkedin.com/in/gabrielsimeonikwor/

📝 License

This project is open source and available under the MIT License
