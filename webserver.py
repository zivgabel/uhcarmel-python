from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, g, abort
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Location, User
import json
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


app = Flask(__name__)
#Connect to Database and create database session
engine = create_engine('mysql+mysqlconnector://root@localhost/uhcameldb?charset=utf8')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@auth.verify_password
def verify_password(username_or_token, password):
    #Try to see if it's a token first
    print 'user is '+username_or_token + ' password is ' + password
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True



@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})



@app.route('/users', methods = ['POST'])
@auth.login_required
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    if username is None or password is None or last_name is None or first_name is None:
        print "missing arguments"
        abort(400) 
        
    if session.query(User).filter_by(username = username).first() is not None:
        print "existing user"
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message':'user already exists'}), 200#, {'Location': url_for('get_user', id = user.id, _external = True)}
        
    user = User(username = username, first_name = first_name, last_name = last_name )
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ 'username': user.username }), 201#, {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/api/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})












@app.route('/uhcarmel/api/v1/locations/JSON')
def showLocations():
    locations = session.query(Location).order_by(asc(Location.name)).all()
    return jsonify(locations= [l.serialize for l in locations])
    
    
@app.route('/uhcarmel/api/v1/locations/new/', methods=['GET','POST'])
def newRestaurant():
    if request.method == 'POST':
            newLocation = Location(name = request.form['name'], altitude = request.form['altitude'], longitude = request.form['longitude'])
            session.add(newLocation)
            flash('New Restaurant %s Successfully Created' % newLocation.name)
            session.commit()
            return redirect(url_for('showLocations'))
    else:
        return render_template('newLocation.html')
            
@app.route('/uhcarmel/api/v1/locations/<int:location_id>/', methods=['GET','PUT','DELETE'])
def ManipulateLocationItem(location_id):
    editedLocation = session.query(Location).filter_by(id = location_id).one()
    if request.method == 'GET':
        return jsonify(editedLocation.serialize)
    if request.method == 'PUT':
        json_a = request.get_json(force=False)
        try:
            rq_name=json_a['name']
            rq_altitude = json_a['altitude']
            rq_longitude = json_a['longitude']
            editedLocation.name=rq_name
            editedLocation.altitude=rq_altitude
            editedLocation.longitude=rq_longitude
        except:
            return jsonify({'error':'Insufficient data'}), 400
            
        try:
            session.add(editedLocation)
            session.commit()
            return jsonify(editedLocation.serialize)
        except:
            return jsonify({'error':'Error updating location'}), 500
            
        
         
        


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 6000)