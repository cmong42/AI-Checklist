from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

DEFAULT_TIMEOUT = int(os.environ.get("AGENT_TIMEOUT", "180"))
MAX_PROMPT_LENGTH = 5000
MAX_TOKENS = 2048

_executor = ThreadPoolExecutor(max_workers=1)

_low_level = None


def get_low_level_agent():
    global _low_level
    if _low_level is None:
        from low_level_coding_agent import LowLevelCodingAgent
        _low_level = LowLevelCodingAgent()
    return _low_level


def validate_json(data, required_fields, field_limits):
    if not data:
        return "Request body must be valid JSON"
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
        if not isinstance(data[field], str) or not data[field].strip():
            return f"Field '{field}' must be a non-empty string"
    for field, max_len in field_limits.items():
        if field in data and len(data[field]) > max_len:
            return f"Field '{field}' exceeds max length of {max_len}"
    return None


def run_with_timeout(fn, timeout):
    future = _executor.submit(fn)
    try:
        return future.result(timeout=timeout)
    except FuturesTimeout:
        raise TimeoutError(f"Agent did not respond within {timeout}s")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "agents": {
            "low_level_coding_agent": "LowLevelCodingAgent",
        },
    })


SKILL_MD_PATH = os.path.join(
    os.path.dirname(__file__), "models", "SKILL.md"
)


@app.route("/api/skill", methods=["GET"])
def skill():
    try:
        with open(SKILL_MD_PATH) as f:
            content = f.read()
        return content, 200, {"Content-Type": "text/markdown; charset=utf-8"}
    except FileNotFoundError:
        return jsonify({"error": "SKILL.md not found"}), 404


@app.route("/api/low-level-coding-agent", methods=["POST"])
def low_level_coding_agent():
    data = request.get_json()
    error = validate_json(data, ["prompt"], {"prompt": MAX_PROMPT_LENGTH})
    if error:
        return jsonify({"error": error}), 400
    max_tokens = min(data.get("max_tokens", 512), MAX_TOKENS)
    try:
        agent = get_low_level_agent()
        result = run_with_timeout(
            lambda: agent.generate(data["prompt"], max_tokens=max_tokens),
            DEFAULT_TIMEOUT,
        )
        return jsonify({"result": result})
    except TimeoutError as e:
        return jsonify({"error": str(e)}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)
