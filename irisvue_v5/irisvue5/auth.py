from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Review, DiaryEntry, Watchlist
from datetime import datetime
import re

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

# ── SIGNUP ────────────────────────────────────────────────────
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('signup.html')
        if len(username) < 3 or len(username) > 30:
            flash('Username must be 3-30 characters.', 'error')
            return render_template('signup.html')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            flash('Username can only contain letters, numbers, and underscores.', 'error')
            return render_template('signup.html')
        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('signup.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('signup.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('signup.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('signup.html')

        # Create user
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome to Irisvue, {username}!', 'success')
        return redirect(url_for('index'))

    return render_template('signup.html')

# ── LOGIN ─────────────────────────────────────────────────────
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password   = request.form.get('password', '')
        remember   = request.form.get('remember') == 'on'

        if not identifier or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')

        # Find by email or username
        user = User.query.filter_by(email=identifier.lower()).first()
        if not user:
            user = User.query.filter_by(username=identifier).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username/email or password.', 'error')
            return render_template('login.html')

    return render_template('login.html')

# ── LOGOUT ────────────────────────────────────────────────────
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ── PROFILE ───────────────────────────────────────────────────
@auth.route('/profile')
@login_required
def profile():
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    diary   = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.watched_at.desc()).all()
    wl      = Watchlist.query.filter_by(user_id=current_user.id).order_by(Watchlist.added_at.desc()).all()
    return render_template('profile.html',
        user=current_user, reviews=reviews,
        diary=diary, watchlist=wl)

@auth.route('/profile/<username>')
def public_profile(username):
    user    = User.query.filter_by(username=username).first_or_404()
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).limit(10).all()
    diary   = DiaryEntry.query.filter_by(user_id=user.id).order_by(DiaryEntry.watched_at.desc()).limit(10).all()
    return render_template('public_profile.html', user=user, reviews=reviews, diary=diary)

# ── DIARY API ─────────────────────────────────────────────────
@auth.route('/api/diary/add', methods=['POST'])
@login_required
def add_to_diary():
    data = request.json
    existing = DiaryEntry.query.filter_by(
        user_id=current_user.id,
        movie_id=data.get('movie_id')
    ).first()
    if existing:
        return jsonify({'status': 'already_logged', 'message': 'Already in your diary'})
    entry = DiaryEntry(
        user_id     = current_user.id,
        movie_id    = data.get('movie_id'),
        movie_title = data.get('movie_title', ''),
        movie_poster= data.get('movie_poster', ''),
        movie_year  = data.get('movie_year', ''),
        rating      = data.get('rating', 0),
        notes       = data.get('notes', ''),
        watched_at  = datetime.utcnow()
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Added to diary'})

@auth.route('/api/diary/remove/<int:movie_id>', methods=['DELETE'])
@login_required
def remove_from_diary(movie_id):
    entry = DiaryEntry.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return jsonify({'status': 'success'})

# ── REVIEW API ────────────────────────────────────────────────
@auth.route('/api/review/add', methods=['POST'])
@login_required
def add_review():
    data = request.json
    existing = Review.query.filter_by(
        user_id=current_user.id,
        movie_id=data.get('movie_id')
    ).first()
    if existing:
        existing.rating      = data.get('rating', existing.rating)
        existing.review_text = data.get('review_text', existing.review_text)
        existing.watch_type  = data.get('watch_type', existing.watch_type)
        db.session.commit()
        return jsonify({'status': 'updated', 'message': 'Review updated'})
    review = Review(
        user_id     = current_user.id,
        movie_id    = data.get('movie_id'),
        movie_title = data.get('movie_title', ''),
        movie_poster= data.get('movie_poster', ''),
        rating      = data.get('rating', 0),
        review_text = data.get('review_text', ''),
        watch_type  = data.get('watch_type', 'first'),
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Review added'})

@auth.route('/api/review/delete/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    review = Review.query.filter_by(id=review_id, user_id=current_user.id).first()
    if review:
        db.session.delete(review)
        db.session.commit()
    return jsonify({'status': 'success'})

# ── WATCHLIST API ─────────────────────────────────────────────
@auth.route('/api/watchlist/toggle', methods=['POST'])
@login_required
def toggle_watchlist():
    data     = request.json
    movie_id = data.get('movie_id')
    existing = Watchlist.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed', 'message': 'Removed from watchlist'})
    item = Watchlist(
        user_id     = current_user.id,
        movie_id    = movie_id,
        movie_title = data.get('movie_title', ''),
        movie_poster= data.get('movie_poster', ''),
        movie_year  = data.get('movie_year', ''),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'status': 'added', 'message': 'Added to watchlist'})

@auth.route('/api/watchlist/check/<int:movie_id>')
@login_required
def check_watchlist(movie_id):
    exists = Watchlist.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    return jsonify({'in_watchlist': bool(exists)})

# ── REVIEWS FOR A MOVIE ───────────────────────────────────────
@auth.route('/api/reviews/<int:movie_id>')
def get_reviews(movie_id):
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.created_at.desc()).limit(20).all()
    return jsonify([{
        'username':    r.user.username,
        'rating':      r.rating,
        'review_text': r.review_text,
        'watch_type':  r.watch_type,
        'date':        r.created_at.strftime('%b %d, %Y'),
    } for r in reviews])
