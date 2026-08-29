"""Entry point: load seed data and start Flask dev server."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("Friends Forever Change Request System")
    print("เปิดเบราว์เซอร์ที่ http://127.0.0.1:8080")
    app.run(debug=True, host="0.0.0.0", port=8080)
