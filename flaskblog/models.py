from datetime import datetime
from flaskblog import db, login_manager, bcrypt
from flask_login import UserMixin
from hashlib import md5
from wtforms import BooleanField, widgets, TextAreaField

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
	id = db.Column(db. Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.png')																																																			
	password = db.Column(db.String(60), nullable=False)
	recipes = db.relationship( 'Recipe', backref='author', lazy=True)
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	admin = db.Column(db.Boolean())
	notes = db.Column(db.UnicodeText)
	followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

	def __init__(self, username, email, password, notes='', admin=False):
		self.username = username
		self.email = email
		self.password = password
		self.admin = admin
		self.notes = notes

	def is_admin(self):
		return self.admin
	
	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

	def followed_recipes(self):
		followed = Recipe.query.join(
			followers, (followers.c.followed_id == Recipe.user_id)).filter(
				followers.c.follower_id == self.id)
		own = Recipe.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Recipe.timestamp.desc())

class Recipe(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	ingredients = db.Column(db.Text, nullable=False)
	recipe = db.Column(db.Text, nullable=False)
	image_file = db.Column(db.String(20), nullable=False)#, default='default.png')	
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	
	def __repr__(self):
		return f"Recipe('{self.name}', '{self.date_posted}')"

class CKTextAreaWidget(widgets.TextArea):
	def __call__(self, field, **kwargs):
		kwargs.setdefault('class_', 'ckeditor')
		return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
	widget = CKTextAreaWidget()