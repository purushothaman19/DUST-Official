import smtplib
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from sqlalchemy.orm import relationship
from functools import wraps
import os

# Initiating Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = "fedaf527c7e3424b9e8d9406a9d69575"
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)

# Connecting to DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///blogs.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

admin = False
login_manager = LoginManager()
login_manager.init_app(app)

MY_EMAIL = 'officialpurushothaman@gmail.com'
MY_PASSWORD = 'purushoth.g'

DUST = {

    "title": "DUST",

    "body": '''As Buttercup, Humperdinck, and the rest of the country continue making plans for the royal wedding, 
    Buttercup begins to regret leaving Westley. He had risked everything to find her, but she had left him anyway. 
    Since his death, she hadn’t allowed herself to truly feel anything, but soon realizes she never stopped loving 
    Westley. She tells Humperdinck that she’d rather die than marry anyone but Westley. Humperdinck lies to Buttercup 
    and assures her that he will send messengers to Westley in order to bring him back to Florin. The reader learns 
    that Humperdinck had hired Vizzini to kidnap Buttercup in the first place in order to start the war with Guilder, 
    and since that failed, he plans to murder Buttercup after the wedding. During this time between Westley’s death, 
    Humperdinck’s plotting and the idea that true love will not win  the author offers several lengthy passages about 
    the unfairness of life.''',

    "sort": "WEBSITE DEVELOPMENT SPACE",

    "img_url": "https://www.linkpicture.com/q/oie_31449114kS7M12G.png"

}

PURUSH = {

    "title": "PURUSH",

    "body": '''Without Vizzini, Inigo can’t formulate a plan to find the six-fingered man who killed his father. In 
    despair, he turns to drink. The day of Buttercup and Humperdinck’s wedding; Fezzik finds Inigo and nurses him 
    back to health. Fezzik explains that Count Rugen, Humperdinck’s confidant, is the six-fingered man whom Inigo has 
    sought for 20 years. Inigo, knowing he can’t make a plan on his own, searches for Westley, the man in black who 
    outwitted Vizzini. He and Fezzik storm the Zoo of Death, only to find Westley (at this point, only recently) 
    dead. Undeterred, Inigo and Fezzik take Westley to Miracle Max, an out-of-work sorcerer who can temporarily raise 
    people from the dead. They ask for a one-hour spell just enough time to stop the wedding and kill Count Rugen but 
    Max, a little rusty on making miracles, realizes after they leave that the spell will only last for 45 minutes. ''',

    "sort": "FOUNDER",

    "img_url": "https://i.picsum.photos/id/237/200/300.jpg?hmac=TmmQSbShHz9CdQm0NkEjx1Dyh_Y984R9LpNrpvH2D_U",

    "back": "https://i.picsum.photos/id/1023/3955/2094.jpg?hmac=AW_7mARdoPWuI7sr6SG8t-2fScyyewuNscwMWtQRawU"

}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.user_id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


class User(UserMixin, db.Model):
    __tablename__ = "User"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(100))

    # This will act like a List of Stories objects attached to each User.
    # The "author" refers to the author property in the Stories class.
    posts = relationship("Stories", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    likes = relationship("Like", back_populates="like_author")

    def get_id(self):
        return self.user_id


# CONFIGURE TABLES
class Stories(db.Model):
    __tablename__ = "all_posts"
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("User.user_id"))

    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    genre = db.Column(db.String(250), nullable=False)
    img_url_part = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")
    likes = relationship("Like", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("all_posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("User.user_id"))
    parent_post = relationship("Stories", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("all_posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("User.user_id"))
    parent_post = relationship("Stories", back_populates="likes")
    like_author = relationship("User", back_populates="likes")
    likes = db.Column(db.Integer)


# db.create_all()
# db.session.commit()

# for i in range(1, 10):
#     users = Comment.query.get(i)
#     print(users)
#     db.session.delete(users)
#     db.session.commit()


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    Genre = StringField("Genre", validators=[DataRequired()])
    img_url_part = StringField("Part Image URL", validators=[URL()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    email = StringField('Email-ID', validators=[DataRequired(message='Enter a valid email-id')])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email-ID', validators=[DataRequired(message='Enter a valid email-id')])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    comment = CKEditorField('Leave a Comment!', validators=[DataRequired(message='Please Type Your Comment')])
    submit = SubmitField('Submit')


@app.route('/')
def home():
    global admin

    try:
        if current_user.user_id == 1:
            admin = True

        else:
            admin = False

    except AttributeError:
        admin = request.args.get('admin')

    all_posts = Stories.query.all()

    title = 'DUST'
    return render_template('index.html', admin=admin, title=title, all_posts=all_posts)


@app.route('/single', methods=['GET', 'POST'])
def single_post():
    global admin, new_like
    # return f'<h1> {admin} </h1>'
    post_id = request.args.get('post_id')
    requested_post = Stories.query.get(post_id)
    admin = request.args.get('admin')
    comment_counts = len(requested_post.comments)
    like_counts = len(requested_post.likes)

    if request.args.get('comment'):
        form = CommentForm()

        if form.validate_on_submit():
            if not current_user.is_authenticated:
                flash("You need to login or register to comment.")
                return redirect(url_for("login"))

            new_comment = Comment(
                text=form.comment.data,
                comment_author=current_user,
                parent_post=requested_post
            )
            db.session.add(new_comment)
            db.session.commit()

            return redirect(url_for('single_post', post_id=post_id, admin=admin, title=requested_post.title))

        return render_template('single.html', admin=admin, post=requested_post, form=form, comment=True,
                               post_id=post_id, title=requested_post.title)

    if request.args.get('like') == 'True':

        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        elif not Like.query.filter_by(author_id=current_user.user_id).first():
            # return f"<h1> {like_counts} </h1>"
            new_like = Like(
                post_id=post_id,
                author_id=current_user.user_id,
                likes=1
            )

            db.session.add(new_like)

        elif Like.query.filter_by(author_id=current_user.user_id).first():
            old = Like.query.filter_by(author_id=current_user.user_id).first()

            like_to_delete = Like.query.get(old.id)
            db.session.delete(like_to_delete)

        db.session.commit()
        like_counts = len(requested_post.likes)

        if request.args.get('home') == "True":
            return redirect(url_for('home'))

        return redirect(url_for('single_post', post_id=post_id, admin=admin, title=requested_post.title))

    return render_template('single.html', admin=admin, post=requested_post, post_id=post_id, ccounts=comment_counts,
                           lcounts=like_counts, title=requested_post.title)


@app.route('/edit', methods=['GET', 'POST'])
@admin_only
def edit_post():
    global admin
    post_id = request.args.get('post_id')
    post = Stories.query.get(post_id)

    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body,
        Genre=post.genre,
        img_url_part=post.img_url_part,
    )

    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        post.genre = edit_form.Genre.data
        post.img_url_part = edit_form.img_url_part.data

        db.session.commit()

        try:
            if current_user.user_id == 1:
                admin = True

            else:
                admin = False

        except AttributeError:
            admin = request.args.get('admin')

        return redirect(url_for("single_post", post_id=post.id, admin=admin))

    return render_template("create_post.html", form=edit_form)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('About.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    errors = []
    # posts = Stories.query.all()

    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email=request.form.get('email'),
            username=request.form.get('name'),
            password=hash_and_salted_password,
        )

        if User.query.filter_by(email=request.form.get('email')).first():
            errors.append("You've already signed up with that email, log in instead!")
            login_form = LoginForm()
            return render_template("login.html", errors=errors, form=login_form)

        elif User.query.filter_by(username=request.form.get('name')).first():
            errors.append('The username has already been taken')
            return render_template("register.html", errors=errors, form=form)

        else:

            errors.clear()

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            with smtplib.SMTP('smtp.gmail.com', 587) as connection:
                connection.starttls()
                connection.login(MY_EMAIL, MY_PASSWORD)
                connection.sendmail(from_addr=MY_EMAIL,
                                    to_addrs=request.form.get('email'),
                                    msg=f"Subject:WELCOME TO DUST\n\nWelcome {request.form.get('name')}! Happy to see"
                                        f"you with us. Thanks for supporting! Keep rocking!".encode('utf-8'))

            return redirect(url_for('home', admin=admin))

    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global admin
    form = LoginForm()
    errors = []

    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            errors.append("That email does not exist, please Register and then come back.")
            return render_template("login.html", errors=errors, form=form)

        # Check stored password hash against entered password hashed.
        if check_password_hash(user.password, password):
            login_user(user)

            if user.user_id == 1:
                admin = True
            else:
                admin = False

            errors.clear()
            return redirect(url_for('home', admin=admin))

        else:
            errors.append('Incorrect Password! Try Again')
            return render_template("login.html", errors=errors, form=form)

    return render_template("login.html", errors=errors, form=form)


@app.route('/new', methods=['GET', 'POST'])
@admin_only
def create_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        # return f'<h1> {form.title.data} </h1>'

        new_post = Stories(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            genre=form.Genre.data,
            date=date.today().strftime("%B %d, %Y"),
            img_url_part=form.img_url_part.data,
        )

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('create_post.html', form=form)


@app.route('/search')
def search_query():
    query = request.args.get('query')
    # return f"<h1> {query} </h1>"
    relates = Stories.query.filter_by(genre=query).first()
    # return f"<h1> {relates} </h1>"
    return render_template('relates.html', query=relates)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home', admin=False))


@app.route('/delete')
@login_required
def delete_post():
    post_id = request.args.get('post_id')
    post_to_delete = Stories.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('single'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    who = request.args.get('title')
    if who == 'DUST':
        return render_template('profile.html', data=DUST)

    if who == 'PURUSH':
        return render_template('profile.html', data=PURUSH)


if __name__ == '__main__':
    app.run(debug=True)
