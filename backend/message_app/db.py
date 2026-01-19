import logging

from flask_sqlalchemy import SQLAlchemy
from .data_classes import Contact, User
from sqlalchemy import create_engine, select, exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

import click
from flask import g
from flask import current_app

from message_app import db_

logger = logging.getLogger(__name__)

def get_db():
	return db_

# Need to test closing of database if using flask_sqlalchemy?
# def close_db(e=None):
# 	db = g.pop('db', None)

# 	if db is not None:
# 		db.close()

def init_db():
	""" Create all tables"""
	db_.drop_all()
	db_.create_all()


from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
	"""Clear the existing data and create new tables."""
	init_db()
	click.echo('Initialized the database.')

def init_app(app):
	""" Register database commands with the Flask app."""
	app.cli.add_command(init_db_command)
	
def has_contact(user, contact):
	""" Checks if user has added contact """
	try:
		return db_.session.scalar(
				select(
					exists().where(
						(Contact.user == user.id) &
						(Contact.contact == contact.id)
					)
				)
		)
	except SQLAlchemyError as e:
		logger.error(f"Database error in has_contact: {e}")
		return False
		

def get_user_by_name(username):
	""" Returns User object of username if exists, else None """
	try:
		return db_.session.scalar(select(User).where(User.user_name == username))
	except SQLAlchemyError as e:
		logger.error(f"Database error in get_user_by_name: {e}")
		return None

def add_contact(user, contact):
	try:
		new_contact = Contact(user=user.id, contact=contact.id)
		db_.session.add(new_contact)
		db_.session.commit()
		return {'success': True, 'message': 'Contact added successfully'}
	except IntegrityError:
		db_.session.rollback()
		return {'success': False, 'message': 'Database constraint violation'}
	except SQLAlchemyError as e:
		db_.session.rollback()
		return {'success': False, 'message': f'Database error occurred: {e}'}
