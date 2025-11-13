# 🍳 Recipe App

**Recipe App** is a simple web application built with **Python** and **Django**.  
It allows users to view, add, and manage recipes while demonstrating Django’s core features such as models, migrations, testing, and admin integration.

---

## 🚀 Features

- Create and store recipes in an **SQLite** database  
- Each recipe includes a name, list of ingredients, cooking time, and difficulty rating  
- Automatically assign difficulty level based on cooking time  
- Manage recipes through the **Django Admin** dashboard  
- Basic automated tests for model fields and methods  

---

## 🧱 Tech Stack

- **Backend:** Django 5.x  
- **Language:** Python 3.x  
- **Database:** SQLite (default)

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LambicJaune/recipe_app.git
   cd recipe_app
   
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate     # macOS/Linux
   venv\Scripts\activate        # Windows

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

4. **Apply migrations:**
   ```bash
   python manage.py migrate

5. **Run the development server:**
   ```bash
   python manage.py runserver

6. **Access the app:**
Open your browser and go to http://localhost:8000

---

## 🧪 Running Tests
To run automated tests for the app:
   ```bash
   python manage.py test
   ```

---

## 👩‍💻 Author

Developed by LambicJaune as part of a Django learning project.
