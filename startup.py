# app/startup.py

def on_startup():
    print("🔄 Initializing system...")

    from db.connection import get_connection
    from db.query_loader import load_queries

    try:
        QUERIES = load_queries("sql/init.sql")
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(QUERIES["create_users"])
        conn.commit()

        print("✅ Database initialized successfully.")

    except Exception as e:
        print("❌ Initialization error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
