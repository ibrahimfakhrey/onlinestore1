from email.policy import default

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)

# create the extension
db = SQLAlchemy()
app.config['SECRET_KEY'] = 'your-very-secret-key'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
# initialize the app with the extension
db.init_app(app)
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

admin=Admin(app)

with app.app_context():
    class User(db.Model,UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        name=db.Column(db.String,  nullable=False)
        password=db.Column(db.String,  nullable=False)
        email=db.Column(db.String,  nullable=False)
        role=db.Column(db.String,  default="user")


    class Product(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name=db.Column(db.String,  nullable=False)
        price=db.Column(db.Float())
        quantity=db.Column(db.Integer)
        image_link=db.Column(db.String(1000))
    db.create_all()
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(User, db.session))

# Flask-Login User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route("/")
def start():
    all_products=Product.query.all()

    return render_template("index.html",products=all_products)


@app.route("/add_product",methods=["GET","POST"])
def add():
    if request.method=="POST":
        name=request.form.get("product_name")
        price=request.form.get("price")
        quantity=request.form.get("quantity")
        image=request.form.get("image")
        new=Product(

            name=name,price=price,quantity=quantity,image_link=image
        )
        db.session.add(new)
        db.session.commit()
        return "added"
    return render_template("add_product.html")


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('login'))

        # Hash the password and create a new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Change here
        new_user = User(name=name, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

if __name__=="__main__":
    app.run(debug=True)