from db.connection import get_connection


def notify_user(user_id, game_id, notif_type, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notifications (user_id, game_id, type, message)
        VALUES (%s, %s, %s, %s)
    """, (user_id, game_id, notif_type, message))
    conn.commit()
    cur.close()
    conn.close()
