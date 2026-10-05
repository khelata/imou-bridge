import os
import threading
import time
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage for the latest command sent to your rover
latest_command = {"action": "stop"}


@app.route("/")
def home():
  return "Imou Rover Bridge Server is Online!"


@app.route("/command", methods=["GET", "POST"])
def command():
  global latest_command
  if request.method == "POST":
    data = request.json
    if data and "action" in data:
      latest_command["action"] = data["action"]
      return jsonify({"status": "success", "command": latest_command["action"]})
    return jsonify({"status": "error", "message": "Invalid data"}), 400
  else:
    # Your rover will GET this endpoint to check what it should do next
    return jsonify(latest_command)


# Self-ping thread to prevent Render free tier from going to sleep
def self_ping():
  app_url = os.environ.get("RENDER_EXTERNAL_URL")
  if not app_url:
    return
  while True:
    time.sleep(300)  # Ping every 5 minutes
    try:
      requests.get(app_url)
    except Exception:
      pass


if __name__ == "__main__":
  # Start the self-ping background thread
  threading.Thread(target=self_ping, daemon=True).start()
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)