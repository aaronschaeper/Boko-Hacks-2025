import re
import bleach
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from models.user import User
from models.note import Note
from datetime import datetime
from extensions import db

notes_bp = Blueprint('notes', __name__, url_prefix='/apps/notes')

def is_valid_password(password):
    """Check if the password meets security requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

@notes_bp.route('/')
def notes():
    """Render notes page with only the logged-in user's notes."""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
    
    return render_template('notes.html', notes=user_notes, current_user_id=current_user.id)

@notes_bp.route('/create', methods=['POST'])
def create_note():
    """Create a new note securely with sanitization to prevent XSS."""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    title = request.form.get('title')
    content = request.form.get('content')

    if not title or not content:
        return jsonify({'success': False, 'error': 'Title and content are required'}), 400

    # Sanitize user input using bleach
    # In this example, no HTML tags are allowed.
    allowed_tags = []   # Change this list if you want to allow specific formatting tags.
    allowed_attrs = {}
    clean_title = bleach.clean(title, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    clean_content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    try:
        note = Note(
            title=clean_title,
            content=clean_content,
            created_at=datetime.now(),
            user_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Note created successfully',
            'note': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': note.user_id
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while saving the note.'}), 500

@notes_bp.route('/search')
def search_notes():
    """Securely search for notes belonging to the logged-in user."""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'success': True, 'notes': []})

    try:
        pattern = "%" + query + "%"
        user_notes = Note.query.filter(
            Note.user_id == current_user.id,
            (Note.title.ilike(pattern)) | (Note.content.ilike(pattern))
        ).order_by(Note.created_at.desc()).all()

        notes = [{
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': note.user_id
        } for note in user_notes]

        return jsonify({'success': True, 'notes': notes})
    except Exception as e:
        return jsonify({'success': False, 'error': 'An error occurred during the search.'}), 500

@notes_bp.route('/delete/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Allow users to delete only their own notes."""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    try:
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()

        if not note:
            return jsonify({'success': False, 'error': 'Note not found or access denied'}), 403

        db.session.delete(note)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Note deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while deleting the note.'}), 500