
import os
import time

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

if not all([DB_NAME, DB_USER, DB_PASSWORD]):
    raise RuntimeError("Database environment variables are missing")

from sqlalchemy.engine import URL

app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }


def initialize_database():
    for attempt in range(10):
        try:
            with app.app_context():
                db.create_all()
            print("Database initialized successfully", flush=True)
            return
        except Exception as exc:
            print(f"Database connection attempt {attempt + 1}: {exc}", flush=True)
            time.sleep(3)

    raise RuntimeError("Could not initialize database")



@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


@app.get("/ready")
def ready():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "ready",
            "database": "connected"
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "not ready",
            "database": "unavailable"
        }), 503



@app.get("/users")
def get_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify([user.to_dict() for user in users]), 200

@app.get("/users/<int:user_id>")
def get_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify(user.to_dict()), 200


@app.post("/users")
def create_user():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    user = User(name=name, email=email)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409


@app.put("/users/<int:user_id>")
def update_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = str(data["name"]).strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400
        user.name = name

    if "email" in data:
        email = str(data["email"]).strip().lower()
        if not email:
            return jsonify({"error": "Email cannot be empty"}), 400
        user.email = email

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409


@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000)
