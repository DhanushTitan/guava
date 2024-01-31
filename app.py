from flask import Flask, render_template, request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = "dskjbsnddjvrnfnjf"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guava3.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Guava(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    kg = db.Column(db.Integer)
    price = db.Column(db.Integer)
    total = db.Column(db.Integer)
    updated = db.Column(db.String)
    

    def __init__(self, name, kg, price, total,updated):
        self.name = name
        self.kg = kg
        self.price = price
        self.total = total
        self.updated = updated

with app.app_context():
    # Create the database tables
    db.create_all()

@app.route('/')
@app.route('/home')
def home():
    total_kg =  db.session.query(Guava.name, db.func.sum(Guava.kg)).all()
    total_amount = db.session.query(Guava.name, db.func.sum(Guava.total)).all()
    return render_template('home.html', total_kg=total_kg, total_amount=total_amount)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        kg = int(request.form['kg'])
        price = int(request.form['price'])
        total = kg * price
        updated = datetime.datetime.now().strftime("%d/%m/%Y")
        guava = Guava(name, kg, price, total, updated)
        db.session.add(guava)
        db.session.commit()
        return redirect(url_for('view'))
       
    return render_template('add.html')


@app.route('/view')
def view():
    guavas = Guava.query.order_by(Guava.updated.desc()).all()
    total_kg =  db.session.query(Guava.name, db.func.sum(Guava.kg)).all()
    # guavas = Guava.query.all()
    return render_template('view.html', guavas=guavas, total_kg=total_kg)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    guava = Guava.query.get_or_404(id)
    if request.method == 'POST':
        guava.name = request.form['name']
        guava.kg = int(request.form['kg'])
        guava.price = int(request.form['price'])
        guava.total = guava.kg * guava.price
        guava.updated = datetime.datetime.now().strftime("%d/%m/%Y")
        db.session.commit()
        
        return redirect(url_for('view', id=id))
    return render_template('edit.html', guava=guava)



@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    guava = Guava.query.filter_by(id=id).first()
    if request.method == 'POST':
        if guava:
            db.session.delete(guava)
            db.session.commit()
            return redirect(url_for('view'))
        return '<h1>Guava with id {id} does not exist</h1>'
    return render_template('delete.html')



@app.route('/total_amount')
def totals():
    query = db.session.query(Guava.name, db.func.sum(Guava.total)).group_by(Guava.name).all()
    return render_template("amount.html", query=query)

@app.route('/total_kg')
def total_kg():
    query = db.session.query(Guava.name, db.func.sum(Guava.kg)).group_by(Guava.name).all()
    return render_template("kg.html", query=query)

