from flask import Blueprint, render_template, redirect, url_for, request, send_from_directory, abort, current_app, send_file
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from .models import Content
from . import db
from sqlalchemy import or_


views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
@login_required
def home():
    if current_user.role == 'teacher':
        return redirect(url_for('views.teacher_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('views.student_dashboard'))
    else:
        return "Role not assigned"
    
@views.route('/teacher')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('views.home'))

    return render_template(
        "teacher_dashboard.html",
        user=current_user
    )

@views.route('/student')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('views.home'))

    query = request.args.get('q')
    selected_subject = request.args.get('subject')

    # Get unique subjects for dropdown
    subjects = (
        Content.query
        .with_entities(Content.subject)
        .distinct()
        .all()
    )
    subjects = [s[0] for s in subjects]  

    contents_query = Content.query

    if query:
        contents_query = contents_query.filter(
            or_(
                Content.subject.ilike(f"%{query}%"),
                Content.chapter.ilike(f"%{query}%"),
                Content.teacher_name.ilike(f"%{query}%")
            )
        )

    if selected_subject:
        contents_query = contents_query.filter(
            Content.subject == selected_subject
        )

    contents = contents_query.all()

    return render_template(
        "student_dashboard.html",
        contents=contents,
        subjects=subjects,
        selected_subject=selected_subject
    )


@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role != 'teacher':
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        subject = request.form.get('subject')
        chapter = request.form.get('chapter')
        file = request.files.get('file')

        if file and file.filename != '':
            # USE THE CONFIG PATH
            base_dir = current_app.config['UPLOAD_FOLDER']
            chapter_folder = os.path.join(base_dir, subject, chapter)
            
            os.makedirs(chapter_folder, exist_ok=True)
            
            filename = secure_filename(file.filename) # Always secure your filenames!
            file_path = os.path.join(chapter_folder, filename)
            file.save(file_path)

            new_content = Content(
                subject=subject,
                chapter=chapter,
                filename=filename,
                youtube_link=request.form.get('youtube'),
                teacher_name=current_user.name
            )
            db.session.add(new_content)
            db.session.commit()
            return redirect(url_for('views.teacher_dashboard'))
    return render_template("upload.html")


@views.route('/download/<int:content_id>')
@login_required
def download_file(content_id):
    content = Content.query.get_or_404(content_id)

    file_path = os.path.join(
        current_app.root_path,
        'uploads',
        content.subject,
        content.chapter,
        content.filename
    )

    return send_file(
        file_path,
        as_attachment=True
    )


@views.route('/preview/<int:content_id>')
@login_required
def preview(content_id):
    content = Content.query.get_or_404(content_id)

    file_url = None
    file_ext = None

    if content.filename:
        file_ext = content.filename.rsplit('.', 1)[-1].lower()
        file_url = url_for('views.serve_file', content_id=content.id)

    return render_template(
        'preview.html',
        content=content,
        file_ext=file_ext,
        file_url=file_url
    )

@views.route('/serve/<int:content_id>')
@login_required
def serve_file(content_id):
    content = Content.query.get_or_404(content_id)

    if not content.filename:
        abort(404)

    file_path = os.path.join(
        current_app.root_path,
        'uploads',
        content.subject,
        content.chapter,
        content.filename
    )

    if not os.path.exists(file_path):
        abort(404)

    return send_file(file_path)
