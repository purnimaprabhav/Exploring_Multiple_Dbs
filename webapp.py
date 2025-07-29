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
        .account-button {
            position: absolute;
            right: 30px;
            top: 25px;
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
            margin-top: 20px;
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

# Main Content
st.markdown("<div class='maincontent'>", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "signup_success" not in st.session_state:
    st.session_state.signup_success = False

if "page" not in st.session_state:
    st.session_state.page = "main"

if st.session_state.logged_in:
    with st.container():
        col1, col2, col3 = st.columns([1, 5, 1])
        with col3:
            option = st.radio("Account", ["Home", "Profile", "Edit Profile", "Logout"], horizontal=True)
            if option == "Logout":
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.page = "main"
                st.rerun()
            elif option == "Profile":
                st.session_state.page = "profile"
                st.rerun()
            elif option == "Edit Profile":
                st.session_state.page = "edit_profile"
                st.rerun()
            elif option == "Home":
                st.session_state.page = "main"
                st.rerun()

    # Profile page logic
    if st.session_state.page == "profile":
        username = st.session_state.username
        user_data = requests.get(f"{API_URL}/neo4j/get_user/{username}")
        if user_data.status_code == 200:
            user = user_data.json()
            st.subheader("Your Profile")
            st.markdown(f"""
                **Name:** {user['name']}  
                **Username:** {user['username']}  
                **Email:** {user['email']}  
                **Phone:** {user['number']}  
                **Role:** {user['role']}  
                **Experience:** {user['experience']} years  
                **Organization:** {user['organization']}  
                **Availability:** {'Yes' if user['availability'] else 'No'}  
                **Skills:** {', '.join(user['skills'])}  
                **Interests:** {', '.join(user['interests'])}
            """)

            # Fetch users with similar interests via new API
            result = requests.get(f"{API_URL}/neo4j/similar_users/{username}")
            if result.status_code == 200:
                similar = result.json()
                if similar:
                    st.markdown("---")
                    st.subheader("Users with Similar Interests")
                    for entry in similar:
                        st.markdown(f"""
                            <div class='user-card'>
                                <h4>{entry['name']}</h4>
                                <p><strong>Common Interests:</strong> {', '.join(entry['common_interests'])}</p>
                                <p><strong>Email:</strong> {entry['email']}</p>
                                <p><strong>Phone:</strong> {entry['number']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No users found with similar interests.")

st.markdown("</div>", unsafe_allow_html=True)
