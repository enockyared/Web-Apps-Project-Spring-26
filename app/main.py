from flask_cors import CORS

from app import create_app
from app.config import get_config

app_config = get_config("development")
app = create_app(app_config)

CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:5173"]}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)

if __name__ == "__main__":
    app.run(debug=True)