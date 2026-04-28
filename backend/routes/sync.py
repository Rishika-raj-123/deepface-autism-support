from flask import Blueprint, request, jsonify
import logging
from services.supabase_service import save_session_data

logger = logging.getLogger(__name__)
sync_bp = Blueprint("sync", __name__)

@sync_bp.route("/sync", methods=["POST"])
def sync():
    """Sync session data from child page to database.
    
    Creates new session if none exists and is_online=True.
    Updates existing session with latest stats.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing data"}), 400
    
    student_id = data.get("studentId")
    if not student_id or student_id == "unknown":
        return jsonify({"status": "ignored", "reason": "no_student_id"}), 200

    elapsed_seconds = data.get("elapsedSeconds", 0)
    distraction_count = data.get("distractionCount", 0)
    is_active = data.get("isOnline", True)

    # Save to Supabase
    try:
        save_session_data(student_id, elapsed_seconds, distraction_count, is_active)
        return jsonify({"status": "success", "session_active": is_active}), 200
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@sync_bp.route("/sync/end", methods=["POST"])
def end_session():
    """End a session - sets is_active=False and records end_time."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing data"}), 400
    
    student_id = data.get("studentId")
    if not student_id or student_id == "unknown":
        return jsonify({"status": "ignored", "reason": "no_student_id"}), 200

    elapsed_seconds = data.get("elapsedSeconds", 0)
    distraction_count = data.get("distractionCount", 0)

    # End the session in Supabase
    try:
        save_session_data(student_id, elapsed_seconds, distraction_count, is_active=False)
        logger.info(f"Session ended for student {student_id}")
        return jsonify({"status": "success", "action": "session_ended"}), 200
    except Exception as e:
        logger.error(f"End session failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@sync_bp.route("/get_latest_session/<child_id>", methods=["GET"])
def get_latest_session(child_id):
    """Get the latest session for a child (active or completed)."""
    from services.supabase_service import fetch_latest_session
    data = fetch_latest_session(child_id)
    if data:
        return jsonify(data), 200
    return jsonify({"error": "No session found or Supabase not configured"}), 404


@sync_bp.route("/children/<parent_id>", methods=["GET"])
def get_children(parent_id):
    """Get all children linked to a parent (bypasses RLS via service role)."""
    from services.supabase_service import fetch_children_by_parent
    data = fetch_children_by_parent(parent_id)
    if data is not None:
        return jsonify(data), 200
    return jsonify({"error": "Failed to fetch children or Supabase not configured"}), 500
