"""
TeleTrack Enterprise — File Upload Routes
Handles file attachments for incidents (evidence, screenshots, configs).
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.supporting import FileAttachment
from models.incident import Incident

files_bp = Blueprint("files", __name__, url_prefix="/api/files")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'csv', 'log', 'conf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    """Upload a file and attach it to an incident."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
        
    file = request.files['file']
    incident_id = request.form.get('incident_id')

    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "File type not allowed"}), 400

    if not incident_id:
        return jsonify({"success": False, "error": "incident_id is required"}), 400

    # Ensure incident exists
    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({"success": False, "error": "Incident not found"}), 404

    # Ensure upload directory exists
    upload_folder = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # Secure filename and add UUID to prevent collisions
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Save the file
    file.save(file_path)
    file_size = os.path.getsize(file_path)
    
    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)
        return jsonify({"success": False, "error": "File size exceeds 10MB limit"}), 400

    # Create DB record
    attachment = FileAttachment(
        incident_id=incident.id,
        filename=unique_filename,
        original_filename=original_filename,
        file_size=file_size,
        mimetype=file.mimetype,
        uploaded_by_id=int(get_jwt_identity())
    )
    
    db.session.add(attachment)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "File uploaded successfully",
        "data": attachment.to_dict()
    }), 201


@files_bp.route("/download/<int:attachment_id>", methods=["GET"])
@jwt_required()
def download_file(attachment_id):
    """Download a file attachment."""
    attachment = FileAttachment.query.get(attachment_id)
    if not attachment:
        return jsonify({"success": False, "error": "Attachment not found"}), 404
        
    upload_folder = os.path.join(current_app.root_path, 'uploads')
    
    return send_from_directory(
        upload_folder,
        attachment.filename,
        as_attachment=True,
        download_name=attachment.original_filename
    )


@files_bp.route("/incident/<int:incident_id>", methods=["GET"])
@jwt_required()
def get_incident_files(incident_id):
    """Get all files attached to an incident."""
    attachments = FileAttachment.query.filter_by(incident_id=incident_id).all()
    return jsonify({
        "success": True,
        "data": [a.to_dict() for a in attachments]
    })
