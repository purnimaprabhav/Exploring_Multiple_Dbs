import streamlit as st
import requests
import os

st.set_page_config(page_title="TeamUp | Home", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Header and Footer Styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Monomakh&display=swap');

        .nav-bar {
            background-color: #1d3557;
            padding: 16px;
            color: white;
            text-align: center;
            font-size: 32px;
            position: fixed;
            top: 10;
            left: 0;
            width: 100%;
            z-index: 1000;
            font-family: 'Monomakh', serif;
        }
        .footer {
            font-family: 'Monomakh', serif;
            background-color: #1d3557;
            padding: 12px;
            color: white;
            text-align: center;
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            font-size: 16px;
        }
        .maincontent {
            margin-top: 100px;
            margin-bottom: 80px;
            padding: 20px;
            font-family: 'Monomakh', serif;
            text-align: center;
        }
        .user-card {
            border: 2px solid #1d3557;
            border-radius: 10px;
            padding: 20px;
            margin: 10px auto;
            background-color: #f1faee;
            width: 60%;
            text-align: left;
        }
    </style>

    <div class="nav-bar">
        Welcome to TeamUp - Find Your Perfect Collaborators
    </div>

    <div class="footer">
        Built for NoSQL Final Project | GitHub: <a href="https://github.com/yourusername/teamup" target="_blank" style="color: white;">TeamUp Repo</a>
    </div>
""", unsafe_allow_html=True)

# Initialize session states
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "signup_success" not in st.session_state:
    st.session_state.signup_success = False
if "page" not in st.session_state:
    st.session_state.page = "main"

# Layout
st.markdown("<div class='maincontent'>", unsafe_allow_html=True)

# Account Controls
if st.session_state.logged_in:
    account_option = st.radio(
        "Account Options",
        ["Home", "Profile", "Edit Profile", "Logout"],
        horizontal=True,
        index=["Home", "Profile", "Edit Profile", "Logout"].index(st.session_state.page if st.session_state.page in ["Home", "Profile", "Edit Profile"] else "Home")
    )

    if account_option == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "main"
        st.rerun()
    elif account_option == "Profile":
        st.session_state.page = "profile"
    elif account_option == "Edit Profile":
        st.session_state.page = "edit_profile"
    elif account_option == "Home":
        st.session_state.page = "main"


if not st.session_state.logged_in:
    with st.expander("🔐 Login"):
        username = st.text_input("Username", key="login_username")
        if st.button("Login"):
            check_response = requests.get(f"{API_URL}/neo4j/user_exists/{username}")
            if check_response.status_code == 200 and check_response.json().get("exists"):
                st.success("Login successful!")
                st.session_state.username = username
                st.session_state.logged_in = True
                st.session_state.page = "main"
                st.rerun()
            else:
                st.error("Username not found. Please sign up first.")

if st.session_state.page == "profile" and st.session_state.logged_in:
    st.subheader("👤 Your Profile")
    profile_resp = requests.get(f"{API_URL}/neo4j/get_user/{st.session_state.username}")
    if profile_resp.status_code == 200:
        user = profile_resp.json()
        availability = user.get("availability", False)
        updated = st.toggle("Available to Join a Team", value=availability)

        if updated != availability:
            toggle_payload = {"username": st.session_state.username, "availability": updated}
            toggle_resp = requests.put(f"{API_URL}/neo4j/update_availability", json=toggle_payload)
            if toggle_resp.status_code == 200:
                st.success("Availability updated successfully.")
                st.rerun()
            else:
                st.error("Failed to update availability.")

        st.markdown(f"""
            <div class='user-card'>
                <h4>{user['name']}</h4>
                <p><strong>Username:</strong> {user['username']}</p>
                <p><strong>Email:</strong> {user['email']}</p>
                <p><strong>Phone:</strong> {user['number']}</p>
                <p><strong>Role:</strong> {user['role']}</p>
                <p><strong>Experience:</strong> {user['experience']} years</p>
                <p><strong>Organization:</strong> {user['organization']}</p>
                <p><strong>Skills:</strong> {', '.join(user['skills'])}</p>
                <p><strong>Interests:</strong> {', '.join(user['interests'])}</p>
                <p><strong>Available:</strong> {'✅' if user['availability'] else '❌'}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Could not load profile.")

elif st.session_state.page == "main" and st.session_state.logged_in:
    st.subheader(f"🔎 Find your Team, {st.session_state.username}")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        role = st.text_input("Desired Role")
    with col2:
        skills = st.text_input("Required Skills (comma-separated)")
    with col3:
        experience = st.slider("Minimum Experience (years)", 0, 30, 1)

    if st.button("Find Matches"):
        payload = {
            "role": role if role else None,
            "skills": [s.strip() for s in skills.split(",") if s.strip()],
            "min_experience": experience
        }
        result = requests.post(f"{API_URL}/neo4j/find_matches", json=payload)
        if result.status_code == 200:
            matches = result.json()
            if matches:
                st.success(f"Found {len(matches)} matching collaborators:")
                for user in matches:
                    st.markdown("""
                        <div class='user-card'>
                            <h4>{name}</h4>
                            <p><strong>Role:</strong> {role}</p>
                            <p><strong>Skills:</strong> {skills}</p>
                            <p><strong>Experience:</strong> {exp} years</p>
                            <p><strong>Available:</strong> {avail}</p>
                            <details>
                                <summary><strong>📞 Contact</strong></summary>
                                <p><strong>Email:</strong> {email}</p>
                                <p><strong>Phone:</strong> {phone}</p>
                            </details>
                        </div>
                    """.format(
                        name=user['name'],
                        role=user['role'],
                        skills=', '.join(user['skills']),
                        exp=user['experience'],
                        avail='✅' if user['availability'] else '❌',
                        email=user['email'],
                        phone=user['number']
                    ), unsafe_allow_html=True)
            else:
                st.info("No matching users found.")
        else:
            st.error("Failed to fetch matches.")

if not st.session_state.logged_in and not st.session_state.signup_success:
    with st.expander("📝 Sign Up"):
        with st.form("signup_form"):
            name = st.text_input("Name")
            new_username = st.text_input("Username")
            number = st.text_input("Phone Number")
            email = st.text_input("Email")
            role = st.text_input("Role")
            skills = st.text_input("Skills (comma-separated)")
            experience = st.slider("Experience (years)", 0, 30, 1)
            interests = st.text_input("Interests (comma-separated)")
            organization = st.text_input("Organization")
            availability = st.radio("Available to join a team?", ["Yes", "No"])

            submitted = st.form_submit_button("Create Account")
            if submitted:
                check_response = requests.get(f"{API_URL}/neo4j/user_exists/{new_username}")
                if check_response.status_code == 200 and check_response.json().get("exists"):
                    st.warning("Username already exists. Please choose a different one.")
                else:
                    payload = {
                        "username": new_username,
                        "name": name,
                        "number": number,
                        "email": email,
                        "role": role,
                        "skills": [s.strip() for s in skills.split(",")],
                        "experience": experience,
                        "interests": [i.strip() for i in interests.split(",")],
                        "organization": organization,
                        "availability": availability == "Yes"
                    }
                    res = requests.post(f"{API_URL}/neo4j/add_user", json=payload)
                    if res.status_code == 200:
                        st.session_state.signup_success = True
                        st.success("User created, login to continue.")
                        st.rerun()
                    else:
                        st.error("Error creating account. Please try again later.")
elif not st.session_state.logged_in and st.session_state.signup_success:
    st.success("User created, login to continue.")

st.markdown("</div>", unsafe_allow_html=True)
