import streamlit as st
import requests

BACKEND_BASE = "http://127.0.0.1:5000"

st.set_page_config(page_title="Social Media Integrator", page_icon="🌐")

st.title("Social Media Integrator")
st.write("Twitter/X integration prototype with Streamlit + Flask.")


st.header("Step 1: Login with Twitter/X")

st.write(
    """
    1. Click the button below.  
    2. A new browser tab will open → Twitter login → then redirect to our backend.  
    3. On the callback page, copy the **access token** from the big textarea.
    """
)

login_url = f"{BACKEND_BASE}/login"
st.link_button("Login with Twitter/X", login_url)


st.header("Step 2: Paste Access Token")

access_token = st.text_area(
    "Paste the access token from the backend callback page:",
    height=150,
)

if "tweets" not in st.session_state:
    st.session_state["tweets"] = None

if st.button("Fetch My Tweets"):
    if not access_token.strip():
        st.error("Please paste the access token first.")
    else:
        with st.spinner("Fetching tweets from backend..."):
            try:
                resp = requests.get(
                    f"{BACKEND_BASE}/tweets",
                    params={"access_token": access_token.strip()},
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state["tweets"] = data.get("data", [])
                    st.success("Tweets fetched successfully!")
                else:
                    st.error(f"Error from backend: {resp.status_code}")
                    st.code(resp.text)
            except Exception as e:
                st.error(f"Request failed: {e}")


st.header("Step 3: View Tweets")

tweets = st.session_state.get("tweets") or []
if not tweets:
    st.info("No tweets loaded yet.")
else:
    for t in tweets:
        st.markdown("---")
        st.markdown(f"**Tweet ID:** `{t.get('id')}`")
        st.write(t.get("text", ""))

