from flask import Flask, redirect, request, jsonify
import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TWITTER_REDIRECT_URI")
SCOPE = os.getenv("TWITTER_SCOPE")
CODE_CHALLENGE = os.getenv("TWITTER_CODE_CHALLENGE")
CODE_VERIFIER = os.getenv("TWITTER_CODE_VERIFIER")


@app.route("/")
def home():
    return "Backend is running. Go to /login from the Streamlit app."


@app.route("/login")
def login():
    """
    Redirect user to Twitter/X authorization page.
    """
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": "random_state_123",  # in real app: generate & validate
        "code_challenge": CODE_CHALLENGE,
        "code_challenge_method": "plain",  # or "S256" if you implement real PKCE
    }

    auth_url = "https://twitter.com/i/oauth2/authorize?" + urlencode(params)
    return redirect(auth_url)


@app.route("/callback")
def callback():
    """
    Twitter/X redirects here with ?code=...
    We exchange that code for an access token.
    """
    error = request.args.get("error")
    if error:
        return f"Error from Twitter: {error}", 400

    code = request.args.get("code")
    if not code:
        return "No authorization code provided.", 400

    token_url = "https://api.twitter.com/2/oauth2/token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": CODE_VERIFIER,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    resp = requests.post(token_url, data=data, headers=headers)
    if resp.status_code != 200:
        return f"Token request failed: {resp.status_code} - {resp.text}", 400

    token_json = resp.json()
    access_token = token_json.get("access_token")

    # For simplicity: we just show the token on the page
    # and you copy-paste it into Streamlit.
    # In a real app: you'd store it in a DB / session.
    return f"""
        <h1>Twitter Login Successful</h1>
        <p>Copy this access token and paste it in the Streamlit app:</p>
        <textarea rows="6" cols="80">{access_token}</textarea>
    """


@app.route("/tweets")
def tweets():
    """
    Minimal API: requires ?access_token=... in query.
    Streamlit will call this endpoint with the pasted token.
    """
    access_token = request.args.get("access_token")
    if not access_token:
        return jsonify({"error": "Missing access_token parameter"}), 400

    # First: get the authenticated user
    user_resp = requests.get(
        "https://api.twitter.com/2/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if user_resp.status_code != 200:
        return jsonify({"error": "Failed to fetch user", "detail": user_resp.text}), 400

    user_id = user_resp.json()["data"]["id"]

    # Then: get tweets for that user
    tweets_resp = requests.get(
        f"https://api.twitter.com/2/users/{user_id}/tweets",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if tweets_resp.status_code != 200:
        return jsonify({"error": "Failed to fetch tweets", "detail": tweets_resp.text}), 400

    return jsonify(tweets_resp.json())


if __name__ == "__main__":
    # Run on port 5000
    app.run(host="127.0.0.1", port=5000, debug=True)
