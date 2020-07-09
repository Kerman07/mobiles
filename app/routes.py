from flask import (flash, redirect, render_template,
                   request, url_for, session)
from flask_login import (login_required, login_user,
                         current_user, logout_user)
from app import app, db
from app.models import Admin, Phone
from app.forms import AdminForm, PhoneForm
import stripe
from config import Config


stripe_keys = {
    'secret_key': Config.STRIPE_SECRET_KEY,
    'publishable_key': Config.STRIPE_PUBLISHABLE_KEY
}

stripe.api_key = stripe_keys['secret_key']


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'cart' not in session:
        session['cart'] = []
    if request.method == 'POST':
        if 'search' in request.form and request.form['search']:
            value = request.form['search']
            tag = f'%{value}%'
            makers = Phone.query.filter(Phone.maker.like(tag))
            models = Phone.query.filter(Phone.model.like(tag))
            phones = makers.union(models)
        elif 'sorting' in request.form:
            if 'price-asc' in request.form['sorting']:
                session['sorting'] = 'price-asc'
                phones = Phone.query.order_by(Phone.price).all()
            elif 'price-desc' in request.form['sorting']:
                session['sorting'] = 'price-desc'
                phones = Phone.query.order_by(Phone.price.desc()).all()
            elif 'abc' in request.form['sorting']:
                session['sorting'] = 'abc'
                phones = Phone.query.order_by(Phone.maker).all()
            elif 'newest' in request.form['sorting']:
                session['sorting'] = 'newest'
                phones = Phone.query.order_by(Phone.timestamp.desc()).all()
        elif 'sorting' in session:
            if 'price-asc' in session['sorting']:
                phones = Phone.query.order_by(Phone.price).all()
            elif 'price-desc' in session['sorting']:
                phones = Phone.query.order_by(Phone.price.desc()).all()
            elif 'abc' in session['sorting']:
                phones = Phone.query.order_by(Phone.maker).all()
            elif 'newest' in session['sorting']:
                phones = Phone.query.order_by(Phone.timestamp.desc()).all()
        return redirect(url_for('home'))
    if 'sorting' not in session:
        phones = Phone.query.order_by(Phone.timestamp.desc()).all()
    if 'cart' in request.form:
        if request.form['cart'] not in session['cart']:
            session['cart'].append(request.form['cart'])
    return render_template('index.html', phones=phones)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if current_user.is_authenticated:
        return redirect(url_for('db_admin'))
    form = AdminForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if not user or user.check_password(form.password.data):
            flash('Invalid username or password !')
            return redirect(url_for('admin'))
        login_user(user)
        return redirect(url_for('db_admin'))
    return render_template('admin.html', form=form)


@app.route('/dbadmin', methods=['GET', 'POST'])
@login_required
def db_admin():
    form = PhoneForm()
    if form.validate_on_submit():
        phone = Phone(maker=form.maker.data, model=form.model.data,
                      img_link=form.img_link.data, specs=form.specs.data,
                      memory=form.memory.data, ram=form.ram.data,
                      price=form.price.data)
        db.session.add(phone)
        db.session.commit()
        flash('Phone successfully added to database !')
        return redirect(url_for('db_admin'))
    return render_template('dbadmin.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/<maker>-<model>', methods=['GET', 'POST'])
def phone_details(maker, model):
    phone = Phone.query.filter(
        Phone.maker == maker, Phone.model == model).first()
    if 'cart' in request.form:
        if request.form['cart'] not in session['cart']:
            session['cart'].append(request.form['cart'])
    return render_template('phone_detail.html', phone=phone)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.form and 'remove' in request.form:
        index = session['cart'].index(request.form['remove'])
        del(session['cart'][index])
    phones = []
    for item in session['cart']:
        maker, model = item.split('-')
        phone = Phone.query.filter(
            Phone.maker == maker, Phone.model == model).first()
        phones.append(phone)
    total = sum(phone.price for phone in phones)
    return render_template('cart.html', phones=phones, total=total)


@app.route('/checkout-<total>')
def checkout(total):
    return render_template('checkout.html', total=total,
                           key=stripe_keys['publishable_key'])


@app.route('/charge', methods=['POST'])
def charge():
    session['cart'] = []
    try:
        amount = 500
        customer = stripe.Customer.create(
            email=request.form['stripeEmail'],
            source=request.form['stripeToken']
        )
        stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Flask Charge'
        )
        return render_template('charge.html', amount=amount)
    except stripe.error.StripeError:
        return render_template('stripe_error.html')
