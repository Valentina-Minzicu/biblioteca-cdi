from waitress import serve
from app import create_app

app = create_app()

if __name__ == "main":
    serve(app, host="0.0.0.0", port=8000)