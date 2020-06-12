# Please check readme.md regularly :) - @_binary
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user

from sqlalchemy import func

from .models import Post, Upvote, User, Follow
from . import db
from .utils import extract

main = Blueprint('main', __name__)


@main.app_errorhandler(404) 
def not_found(e): 
  
# defining function 
  return render_template("404_default.html") 

@main.route('/')
def index():
	return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
	return redirect(url_for('main.public_profile', username=current_user.name))


@main.route('/public/profile/<username>')
@login_required
def public_profile(username):
  posts = Post.query.filter_by(username=username)
  user = User.query.filter_by(name=username).first()
  if user is None:
    return render_template('404_publicprofile.html')


  my_upvotes = db.session.query(Upvote.id_post).filter(Upvote.upvoter == current_user.name).all()
  my_upvotes = extract(my_upvotes)
  if posts:
    for post in posts:
      if post.id in my_upvotes:
        post.upvote = 'Downvote'
      else:
        post.upvote = 'Upvote'

  followable = Follow.query.filter_by(
      follower=current_user.name, followed=username).first()
  if followable is None:
    followable_style = 'is-info'
    followable = 'Follow'
  else:
    followable_style = 'is-danger'
    followable = 'Unfollow'

  user_upvotes = db.session.query(func.sum(
      Post.upvotes)).filter(Post.username == username).one()[0]
  user_followers = db.session.query(func.count(
      Follow.follower)).filter(Follow.followed == username).one()[0]
  if user_upvotes is None:
    user_upvotes = 0

  return render_template(
      'public_profile.html',
      posts=posts,
      user=user,
      user_upvotes=user_upvotes,
      user_followers = user_followers,
      followable=followable,
      followable_style=followable_style)


@main.route('/posts')
@login_required
def posts():
  posts = Post.query.order_by(Post.upvotes.desc()).all()
  my_upvotes = db.session.query(Upvote.id_post).filter(Upvote.upvoter == current_user.name).all()
  my_upvotes = extract(my_upvotes)
  button = {'text':'Veja somente pessoas que você segue', 'url': url_for('main.posts_followed') }
  if posts:
    for post in posts:
      if post.id in my_upvotes:
        post.upvote = 'Downvote'
      else:
        post.upvote = 'Upvote'
    
    error = None
  else:
    error = 'You don\'t have any content.'
  return render_template('posts.html', posts=posts, button = button, error = error)

@main.route('/posts/followed')
@login_required
def posts_followed():
  posts = db.session.query(Post).join(Follow, Post.username == Follow.followed).filter(Follow.follower == current_user.name).order_by(Post.upvotes.desc()).all()
  my_upvotes = db.session.query(Upvote.id_post).filter(Upvote.upvoter == current_user.name).all()
  my_upvotes = extract(my_upvotes)
  button = {'text':'Veja todas as postagens', 'url': url_for('main.posts') }
  if posts:
    for post in posts:
      if post.id in my_upvotes:
        post.upvote = 'Downvote'
      else:
        post.upvote = 'Upvote'
    error = None
  else: 
    error = 'You don\'t have any followed content.'
  return render_template('posts.html', posts=posts, button = button, error = error)

@main.route('/deletePost/<int:id_post>', methods=['GET'])
@login_required
def deletePost(id_post):
	post = Post.query.filter_by(id=id_post).first()
	if current_user.name == post.username or current_user.name == "admin1":
		db.session.delete(post)
		db.session.query(Upvote).filter(Upvote.id_post == id_post).delete()
		db.session.commit()
	return redirect(request.referrer)


@main.route('/upvote/<int:id_post>', methods=['GET'])
@login_required
def upvote(id_post):
	#print(request.form['link'])
	upvotable = Upvote.query.filter_by(
	    upvoter=current_user.name, id_post=id_post).first()

	if upvotable is None:
		post = Post.query.filter_by(id=id_post).first()
		create_upvote = Upvote(id_post=id_post, upvoter=current_user.name)
		# deleted sqlite file, this restarted us database
		post.upvotes += 1
		db.session.add(create_upvote)
		db.session.commit()
	else:
		post = Post.query.filter_by(id=id_post).first()
		db.session.delete(upvotable)
		db.session.query(Upvote).filter(Upvote.id_post == id_post).delete()
		post.upvotes -= 1
		db.session.commit()
	return redirect(request.referrer)


@main.route('/follow/<username>', methods=['GET'])
@login_required
def follow(username):
	followable = Follow.query.filter_by(
	    follower=current_user.name, followed=username).first()

	if followable is None:
		create_follow = Follow(follower=current_user.name, followed=username)
		# deleted sqlite file, this restarted us database

		db.session.add(create_follow)
		db.session.commit()
	else:
		db.session.delete(followable)
		db.session.commit()
	return redirect(request.referrer)


@main.route('/editPost/<int:id_post>', methods=['GET', 'POST'])
@login_required
def editPost(id_post):
	post = Post.query.filter_by(id=id_post).first()
	title = post.title
	description = post.description
	link = post.link

	if request.method == 'GET':
		return render_template(
		    "makepost.html",
		    title=title,
		    description=description,
		    link=link,
		    url=url_for('main.editPost', id_post=id_post))

	post.title = title = request.form['title']
	post.description = request.form['description']
	post.link = request.form['link']
	db.session.commit()
	return redirect("/posts")
	#return render_template("makepost.html", title = post.title, description=post.description, link = post.link, url =  url_for('main.editPost',id_post = id_post))


@main.route('/makepost', methods=['GET', 'POST'])
@login_required
def makepost():
	if request.method == 'GET':
		return render_template(
		    'makepost.html',
		    name=current_user.name,
		    url=url_for('main.makepost'))
	if request.method == 'POST':
		if request.form['title'] == '' or request.form['description'] == '':
			return redirect("/makepost")  

		create_post = Post(
		    username=current_user.name,
		    title=request.form['title'],
		    description=request.form['description'],
		    link=request.form['link'])
		db.session.add(create_post)
		db.session.commit()
		return redirect("/posts")