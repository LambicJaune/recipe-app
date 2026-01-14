# 🍳 Recipe App

**Recipe App** is a simple web application built with **Python** and **Django**  
that allows users to create, browse, search, and analyze cooking recipes.
It demonstrates core Django concepts such as authentication, class-based views, ORM queries, forms, testing, and production deployment.

---

## 🚀 Features

- User authentication (signup, login, logout)
- Create, view, and manage recipes
- Advanced recipe search and filtering:
  - Name
  - Ingredients
  - Difficulty level
  - Maximum cooking time
- Automatic difficulty calculation based on cooking time and ingredients
- Recipe analytics and visualizations (charts)
- User profile management (profile update & password change)
- **Django Admin** integration
- Automated tests for models and views

---

## 🧱 Tech Stack

- **Backend:** Django 5.x  
- **Language:** Python 3.x  
- **Database:** 
    - SQLite (default for local development)
    - PostgreSQL (production via Neon)
- **Data Processing:** Pandas
- **Deployment:** Heroku
- **Static Files:** WhiteNoise
- **Server:** Gunicorn

---

## ⚙️ Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/LambicJaune/recipe_app.git
   cd recipe_app
   ```
   
2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate     # macOS/Linux
   venv\Scripts\activate        # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a .env file in the project root:

   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=127.0.0.1,localhost
   ```

   ⚠ Do not commit your `.env` file. Make sure it is listed in `.girignore`.

5. **Apply migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser:**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

8. **Access the app:**
Open your browser and go to http://localhost:8000

---

## 🧪 Running Tests
To run automated tests for the app:

   ```bash
   python manage.py test
   ```

---

## 🚀 Deployment (Heroku + Neon)

This project is configured for production deployment using:

**Heroku** (application hosting)

**Neon** (PostgreSQL database)

Deployment requires setting the following environment variables in Heroku:

   - SECRET_KEY

   - DEBUG=False

   - DATABASE_URL

   - ALLOWED_HOSTS

After deployment, run:

   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```


## 👩‍💻 Author

Developed by LambicJaune as part of a Django portfolio project.
