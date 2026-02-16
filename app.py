# main app file

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Book, Sale
import os

# app config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'bookstore-portal-secure-key'

db.init_app(app)

# login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the system.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader # loads the user object from the user ID stored in the session
def load_user(user_id):
    return User.query.get(int(user_id))

# create tables and default data on first run
with app.app_context():
    db.create_all()
    
    # default admin account
    if User.query.count() == 0:
        admin = User(username='Brenda B')
        admin.set_password('chebet05')
        db.session.add(admin)
        db.session.commit()
    
    # sample books
    if Book.query.count() == 0:
        books = [
            Book(title='Ugly Love', author='Colleen Hoover', isbn='978-1476770383', price=850.0, stock_quantity=15, category='Romance', image_url='pics/ugly love.webp'),
            Book(title='The Psychology of Money', author='Morgan Housel', isbn='978-0857197689', price=1500.0, stock_quantity=10, category='Finance', image_url='pics/money.jpg'),
            Book(title='Atomic Habits', author='James Clear', isbn='978-0735211292', price=1000.0, stock_quantity=5, category='Self-Help', image_url='pics/atomic habits.webp'),
            Book(title='Calculus', author='James Stewart', isbn='978-1285740621', price=2500.0, stock_quantity=3, category='Education', image_url='pics/calculus.webp')
        ]
        db.session.bulk_save_objects(books)
        db.session.commit()


# login page - checks username and password
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')


# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# dashboard - shows stats and latest books
@app.route('/')
@login_required
def index():
    total_books = Book.query.count()
    low_stock_count = Book.query.filter(Book.stock_quantity < 5).count()
    
    # get todays revenue
    from datetime import datetime, date
    today = date.today()
    today_sales = db.session.query(db.func.sum(Sale.total_price)).filter(db.func.date(Sale.sale_date) == today).scalar() or 0
    
    latest_books = Book.query.order_by(Book.id.desc()).limit(8).all()
    return render_template('index.html', latest_books=latest_books, total_books=total_books, low_stock_count=low_stock_count, today_sales=today_sales)


# inventory - lists all books in a table
@app.route('/inventory')
@login_required
def inventory():
    books = Book.query.all()
    low_stock = Book.query.filter(Book.stock_quantity < 5).all()
    return render_template('inventory.html', books=books, low_stock=low_stock)


# add new book (CREATE)
@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        category = request.form.get('category')
        
        new_book = Book(title=title, author=author, isbn=isbn, price=price, stock_quantity=stock, category=category)
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('inventory'))
    return render_template('add_book.html')


# edit a book (UPDATE)
@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.isbn = request.form.get('isbn')
        book.price = float(request.form.get('price'))
        book.stock_quantity = int(request.form.get('stock'))
        book.category = request.form.get('category')
        db.session.commit()
        flash(f'"{book.title}" updated successfully!', 'success')
        return redirect(url_for('inventory'))
    return render_template('edit_book.html', book=book)


# remove a book (DELETE)
@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    title = book.title
    Sale.query.filter_by(book_id=book.id).delete()  # delete its sales first
    db.session.delete(book)
    db.session.commit()
    flash(f'"{title}" removed from inventory.', 'success')
    return redirect(url_for('inventory'))


# sell a book - reduces stock and saves the sale
@app.route('/sell_book/<int:book_id>', methods=['POST'])
@login_required
def sell_book(book_id):
    book = Book.query.get_or_404(book_id)
    quantity = int(request.form.get('quantity', 1))
    
    if book.stock_quantity >= quantity:
        book.stock_quantity -= quantity
        sale = Sale(book_id=book.id, quantity=quantity, total_price=book.price * quantity)
        db.session.add(sale)
        db.session.commit()
        flash(f'Sold {quantity} copies of {book.title}', 'success')
    else:
        flash('Not enough stock!', 'danger')
    return redirect(url_for('inventory'))


# search books by title, author or isbn
@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if query:
        results = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) | 
            (Book.author.ilike(f'%{query}%')) | 
            (Book.isbn.ilike(f'%{query}%'))
        ).all()
    else:
        results = []
    return render_template('search_results.html', results=results, query=query)


# transaction logs - all sales, newest first
@app.route('/transactions')
@login_required
def transactions():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return render_template('transactions.html', sales=sales)


# reports - total revenue and top selling books
@app.route('/reports')
@login_required
def reports():
    total_sales = db.session.query(db.func.sum(Sale.total_price)).scalar() or 0
    top_selling = db.session.query(
        Book.title, db.func.sum(Sale.quantity).label('total_sold')
    ).join(Sale).group_by(Book.id).order_by(db.desc('total_sold')).limit(5).all()
    return render_template('reports.html', total_sales=total_sales, top_selling=top_selling)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
