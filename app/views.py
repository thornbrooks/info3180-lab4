import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm
from werkzeug.security import check_password_hash


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        file = form.photo.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('File Saved', 'success')
        return redirect(url_for('files'))

    return render_template('upload.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = UserProfile.query.filter_by(username=username).first()

        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            flash('You have successfully logged in.', 'success')
            return redirect(url_for("upload"))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template("login.html", form=form)


@app.route('/files')
@login_required
def files():
    """Render a page that lists all uploaded image files."""
    images = get_uploaded_images()
    return render_template('files.html', images=images)


@app.route('/uploads/<filename>')
def get_image(filename):
    """Return a specific image from the uploads folder."""
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)


###
# Helper Functions
###

def get_uploaded_images():
    """Iterate over uploads folder and return list of image filenames."""
    images = []
    upload_folder = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    for subdir, dirs, files_list in os.walk(upload_folder):
        for file in files_list:
            images.append(file)
    return images


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()


###
# The functions below should be applicable to all Flask apps.
###

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404