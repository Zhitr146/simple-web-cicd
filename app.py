"""
simple-web-cicd - A simple Flask web application for CI/CD practice.
Provides basic REST API endpoints for greeting, arithmetic, and health check.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Welcome to simple-web-cicd!",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/hello": "Greeting endpoint",
            "/api/add": "Add two numbers (a, b)",
            "/api/multiply": "Multiply two numbers (a, b)"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "simple-web-cicd"}), 200


@app.route("/hello", methods=["GET"])
def hello():
    name = request.args.get("name", "World")
    return jsonify({"message": f"Hello, {name}!"})


@app.route("/api/add", methods=["GET", "POST"])
def api_add():
    a, b = _get_numbers(request)
    if a is None or b is None:
        return jsonify({"error": "Please provide 'a' and 'b' as numbers"}), 400
    return jsonify({"a": a, "b": b, "operation": "add", "result": a + b})


@app.route("/api/multiply", methods=["GET", "POST"])
def api_multiply():
    a, b = _get_numbers(request)
    if a is None or b is None:
        return jsonify({"error": "Please provide 'a' and 'b' as numbers"}), 400
    return jsonify({"a": a, "b": b, "operation": "multiply", "result": a * b})


def _get_numbers(req):
    a = b = None
    data = {}
    if req.method == "POST":
        data = req.get_json(silent=True) or {}
    try:
        raw_a = data.get("a") if data else req.args.get("a")
        raw_b = data.get("b") if data else req.args.get("b")
        if raw_a is not None and raw_b is not None:
            a = float(raw_a)
            b = float(raw_b)
            if a.is_integer() and b.is_integer():
                a, b = int(a), int(b)
    except (TypeError, ValueError):
        return None, None
    return a, b


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)