from flask import Blueprint, g, request, session, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from message_app.data_classes import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from . import db_

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
	# TO DO: Validate usernames
	username = request.json['username']
	password = request.json['password']
	error = None

	# TO DO: React should ensure that empty username and passwords aren't sent?
	# Consider doing all validation on backend. 
	if not username:
		error = 'Username is required.'
	elif not password:
		error = 'Password is required.'

	if error is None:
		try:
			new_user = User(
				user_name = username,
				user_pwd = generate_password_hash(password)
			)
			db_.session.add(new_user)
			db_.session.commit()
			data = {'status': 'success'}
			return jsonify(data)
		
		except IntegrityError:
			# Undo changes so that db gets back to consistent state
			db_.session.rollback()
			error = f"{username} is not available."
			data = {'error': error}
			return jsonify(data)
			
	else:
			# This is unnecessary IF React ensures empty usernames/passwords aren't sent
			data = {'error': error}
			return jsonify(data)

@bp.route('/login', methods=['POST'])
def login():
	username = request.json['username']
	password = request.json['password']
	error = None
	user = db_.session.scalar(select(User).where(User.user_name == username))

	if user is None or not check_password_hash(user.user_pwd, password):
		error = 'Credentials not valid.'
		data = {'error': error}
		return jsonify(data)

	if error is None:
		login_user(user)
		data = {
			'status': 'success',
			'user': {
				'username': user.user_name,
				'uuid': user.uuid
			}
		}
		return jsonify(data)

@bp.route('/current-user', methods=['GET'])
@login_required
def get_current_user():
    user_data = {
        'username': current_user.user_name,
        'uuid': current_user.uuid
    }
    return jsonify(user_data)

@bp.before_app_request
def load_logged_in_usr():
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else:
		g.user = db_.session.query(User).filter_by(id=user_id).first()

@bp.route('/logout', methods=['GET'])
def logout():
    try:
        username = current_user
        print(f'Logging out {username.user_name}')
    except:
        username = None
    logout_user()
    return jsonify({'data': 'success'})
