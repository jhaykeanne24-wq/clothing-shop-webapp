# Clothing Shop Web Application

A complete e-commerce web application for an online clothing store, built with Flask (Python backend), HTML/CSS/Bootstrap (responsive frontend), and MySQL database.

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: MySQL
- **Server**: Flask development server

## Required Features Implemented

1. **Own Logo & Branding** - Custom clothing store branding with consistent color scheme
2. **Index/Home Page** - Public landing page introducing the store
3. **Registration** - Secure user account creation with validation
4. **Login** - Authenticated user login with session management
5. **Web Security** - Password hashing, CSRF protection, SQL injection prevention
6. **Session Management** - Persistent user sessions across pages
7. **SMTP (Email Integration)** - Email notifications for orders and account actions
8. **Dashboard** - User dashboard with order history and activity
9. **Profile Management** - User account details and profile editing
10. **CRUD Functionality** - Full Create, Read, Update, Delete for clothing products
11. **Responsive UI** - Mobile and desktop responsive design with Bootstrap
12. **Form Validation & Error Handling** - Client and server-side validation
13. **Object-Oriented Programming** - OOP principles in Flask backend structure

## Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/jhaykeanne24-wq/clothing-shop-webapp.git
   cd clothing-shop-webapp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create MySQL database**
   ```bash
   mysql -u root -p
   CREATE DATABASE clothing_shop;
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=mysql+pymysql://username:password@localhost/clothing_shop
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   ```

5. **Initialize the database**
   ```bash
   python
   >>> from app import db, create_app
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   Open your browser and navigate to `http://localhost:5000`