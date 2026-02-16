# B-Portal | Online Bookstore Inventory Management System

A professional internal management system designed to track inventory, log sales, and provide business analytics for an online bookstore.

## System Features

### 1. Authentication
*   Secure login and logout system.
*   Protected routes (login required to access any part of the system).
*   Encrypted password storage using Werkzeug security.

### 2. Inventory Management (CRUD)
*   **Create:** Add new books to the system with title, author, ISBN, price, and stock levels.
*   **Read:** View the entire inventory in a searchable, responsive table.
*   **Update:** Edit existing book details including stock levels and pricing.
*   **Delete:** Remove books and their associated history from the system.

### 3. Sales & Transactions
*   **Quick Sell:** Sell books directly from the inventory list with real-time stock updates.
*   **Transaction Logs:** A detailed audit trail of all sales, showing timestamps, quantities, and values.
*   **Low Stock Alerts:** Automatic warnings throughout the system when stock levels fall below a threshold.

### 4. Dashboard & Analytics
*   **Business Overview:** Key metrics visible upon login (Total Inventory, Low Stock counts, and Today's Revenue).
*   **Reports:** Detailed sales analytics showing total revenue generated and a list of the top 5 best-selling books.

## Technical Stack
*   **Backend:** Python / Flask
*   **Database:** SQLAlchemy / SQLite
*   **Frontend:** HTML5, CSS3, JavaScript
*   **Styling:** Bootstrap 5 & FontAwesome 4.7
*   **Authentication:** Flask-Login

## Setup Instructions

1.  **Install Dependencies:**
    ```bash
    pip install flask flask-sqlalchemy flask-login
    ```

2.  **Run the Application:**
    ```bash
    python app.py
    ```

3.  **Access the System:**
    Open your browser and navigate to `http://127.0.0.1:5000`

## Initial Credentials
*   **Username:** Brenda B
*   **Password:** chebet05

---
*Note: This system is intended for internal inventory management and auditing purposes.*
