import logging
import requests
import config

logger = logging.getLogger(__name__)

def get_supabase_headers():
    return {
        "apikey": config.SUPABASE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def save_session_data(student_id, elapsed_seconds, distraction_count, is_active=True):
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        logger.warning("Supabase not configured - skipping session save")
        return
    
    url = f"{config.SUPABASE_URL}/rest/v1"
    headers = get_supabase_headers()
    
    try:
        # 1. Resolve child_id from student_id (child_user_id)
        child_res = requests.get(
            f"{url}/children?child_user_id=eq.{student_id}&select=id",
            headers=headers
        )
        child_data = child_res.json()
        
        if child_data and len(child_data) > 0:
            child_record_id = child_data[0]["id"]
        else:
            child_record_id = student_id

        # 2. Check for existing active session
        session_res = requests.get(
            f"{url}/sessions?child_id=eq.{child_record_id}&is_active=eq.true&select=id,start_time",
            headers=headers
        )
        session_data = session_res.json()
        
        if session_data and len(session_data) > 0:
            session_id = session_data[0]["id"]
            
            # Prepare update data
            data = {
                "child_id": child_record_id,
                "focus_duration": elapsed_seconds,
                "break_count": distraction_count,
                "is_active": is_active
            }
            
            # If session is ending (is_active=False), set end_time
            if not is_active:
                from datetime import datetime, timezone
                data["end_time"] = datetime.now(timezone.utc).isoformat()
            
            # Update existing session
            res = requests.patch(
                f"{url}/sessions?id=eq.{session_id}",
                headers=headers,
                json=data
            )
            if res.status_code in [200, 204]:
                logger.info(f"Updated session {session_id} for child {child_record_id}")
            else:
                logger.error(f"Failed to update session: {res.status_code} - {res.text}")
        else:
            # No active session - create new one only if is_active=True
            if is_active:
                from datetime import datetime, timezone
                data = {
                    "child_id": child_record_id,
                    "focus_duration": elapsed_seconds,
                    "break_count": distraction_count,
                    "is_active": True,
                    "start_time": datetime.now(timezone.utc).isoformat()
                }
                res = requests.post(
                    f"{url}/sessions",
                    headers=headers,
                    json=data
                )
                if res.status_code in [200, 201]:
                    logger.info(f"Created new session for child {child_record_id}")
                else:
                    logger.error(f"Failed to create session: {res.status_code} - {res.text}")
            else:
                logger.info(f"No active session to update for child {child_record_id}")
            
    except Exception as e:
        logger.error(f"Error saving session to Supabase: {e}")

def fetch_latest_session(child_id):
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        return None
    
    url = f"{config.SUPABASE_URL}/rest/v1"
    headers = get_supabase_headers()
    
    try:
        res = requests.get(
            f"{url}/sessions?child_id=eq.{child_id}&order=created_at.desc&limit=1",
            headers=headers
        )
        data = res.json()
        if data and len(data) > 0:
            return data[0]
    except Exception as e:
        logger.error(f"Error fetching session from Supabase: {e}")
    return None


def fetch_children_by_parent(parent_id):
    """Fetch children linked to a parent."""
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        logger.warning("Supabase not configured - cannot fetch children")
        return None
    
    url = f"{config.SUPABASE_URL}/rest/v1"
    headers = get_supabase_headers()
    
    try:
        res = requests.get(
            f"{url}/children?parent_id=eq.{parent_id}&select=*",
            headers=headers
        )
        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"Failed to fetch children: {res.status_code} - {res.text}")
            return None
    except Exception as e:
        logger.error(f"Error fetching children from Supabase: {e}")
        return None
