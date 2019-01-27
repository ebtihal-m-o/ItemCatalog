# Reference --> https://github.com/udacity/ud330.git #
# Reference --> https://github.com/Hisham-Developer/linux-server-configuration#

from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from DB import Base, Brand, ProdactName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "Brand Prodact Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///brand.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state tokennewProdactName


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# connect Google


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
 # user image and  welcom massege
    output = ''
    output += '<h5>Welcome, '
    output += login_session['username']
    output += '!</h5>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; ' \
              'height: 150px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except BaseException:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view brand Information
@app.route('/brand/<int:brand_id>/prodact/JSON')
def brandMenuJSON(brand_id):
    brand = session.query(Brand).filter_by(id=brand_id).one()
    names = session.query(ProdactName).filter_by(
        brand_id=brand_id).all()
    return jsonify(ProdactNames=[i.serialize for i in names])


@app.route('/brand/<int:brand_id>/prodact/<int:prodact_id>/JSON')
def prodactNameJSON(brand_id, prodact_id):
    prodactName = session.query(ProdactName).filter_by(id=prodact_id).one()
    return jsonify(ProdactName=prodactName.serialize)


@app.route('/brand/JSON')
def brandsJSON():
    brands = session.query(Brand).all()
    return jsonify(brands=[r.serialize for r in brands])

# Show all brands


@app.route('/')
@app.route('/brand/')
def showBrands():
    brands = session.query(Brand).order_by(asc(Brand.name))
    if 'username' not in login_session:
        return render_template('publicbrands.html', brands=brands)
    else:
        return render_template('brands.html', brands=brands)
# Create a new brand


@app.route('/brand/new/', methods=['GET', 'POST'])
def newBrand():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBrand = Brand(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newBrand)
        flash('New Brand %s Successfully Created' % newBrand.name)
        session.commit()
        return redirect(url_for('showBrands'))
    else:
        return render_template('newBrand.html')


# Show a brand prodact


@app.route('/brand/<int:brand_id>/')
@app.route('/brand/<int:brand_id>/prodact/')
def showMenu(brand_id):
    brand = session.query(Brand).filter_by(id=brand_id).first()
    names = session.query(
        ProdactName).filter_by(brand_id=brand_id).all()
    return render_template('prodactnames.html', brand=brand, names=names)


# Create new prodact name
@app.route(
    '/brand/<int:brand_id>/prodact/new/', methods=['GET', 'POST'])
def newProdactName(brand_id):
    if 'username' not in login_session:
        return redirect('/login')
    brand = session.query(Brand).filter_by(id=brand_id).first()
    if login_session['user_id'] != brand.user_id:
        flash('Unauthorized, please sing in with the email that '
              'you use to create this brand...!')
        return redirect(url_for('showBrands'))

    if request.method == 'POST':
        newName = ProdactName(name=request.form['name'],
                            description=request.form['description'],
                            price=request.form['price'],
                            brand_id=brand_id)
        session.add(newName)
        session.commit()
        flash("Prodact Name has been added")
        return redirect(url_for('showMenu', brand_id=brand_id))
    else:
        return render_template('newprodactname.html', brand_id=brand_id)
    return render_template('newprodactname.html', brand=brand)


# Edit a Mvoie name
@app.route(
    '/brand/<int:brand_id>/prodact/<int:prodact_id>/edit',
    methods=['GET', 'POST'])
def editProdactName(brand_id, prodact_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedName = session.query(ProdactName).filter_by(id=prodact_id).first()
    brand = session.query(Brand).filter_by(id=brand_id).first()
    if login_session['user_id'] != brand.user_id:
        flash('Unauthorized, please sing in with the email that '
              'you use to create this brand...!')
        return redirect(url_for('showBrands'))
    if request.method == 'POST':
        if request.form['name']:
            editedName.name = request.form['name']
        if request.form['description']:
            editedName.description = request.form['description']
        if request.form['price']:
            editedName.price = request.form['price']
        session.add(editedName)
        session.commit()
        flash('Prodact Name Successfully Edited')
        return redirect(url_for('showMenu', brand_id=brand_id))
    else:
        return render_template(
            'editprodactname.html',
            brand_id=brand_id,
            prodact_id=prodact_id,
            name=editedName)
# Delete prodact name


@app.route('/brand/<int:brand_id>/prodact/<int:prodact_id>/delete',
           methods=['GET', 'POST'])
def deleteProdactName(brand_id, prodact_id):
    if 'username' not in login_session:
        return redirect('/login')
    brand = session.query(Brand).filter_by(id=brand_id).first()
    nameToDelete = session.query(ProdactName).filter_by(id=prodact_id).first()
    if login_session['user_id'] != brand.user_id:
        flash('Unauthorized, please sing in with the email that '
              'you use to create this brand...!')
        return redirect(url_for('showBrands'))
    if request.method == 'POST':
        session.delete(nameToDelete)
        session.commit()
        flash('Prodact Name Successfully Deleted')
        return redirect(url_for('showMenu', brand_id=brand_id))
    else:
        return render_template('deleteprodactname.html', name=nameToDelete)

# Disconnect based on provider


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showBrands'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showBrands'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

