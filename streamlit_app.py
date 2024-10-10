import streamlit as st
from time import sleep
import streamlit_authenticator as stauth
from navigation import make_sidebar
from data_processing import finalize_data

# Fetch the credentials and survey data
df_survey, df_creds = finalize_data()

# Process `df_creds` to extract credentials in the required format
def extract_credentials(df_creds):
    credentials = {
        "credentials": {
            "usernames": {}
        },
        "cookie": {
            "name": "growth_center",
            "key": "growth_2024",
            "expiry_days": 30
        }
    }
    for index, row in df_creds.iterrows():
        credentials['credentials']['usernames'][row['username']] = {
            'name': row['name'],      # Add the 'name' field
            'password': row['password'],  # Password should already be hashed
            'email': row['email'],    # Add the 'email' field
            'unit': row['unit']       # Store the user's unit for later filtering
        }
    return credentials

# Extract credentials from df_creds
credentials = extract_credentials(df_creds)

# Authentication Setup
authenticator = stauth.Authenticate(
    credentials['credentials'],
    credentials['cookie']['name'],
    credentials['cookie']['key'],
    credentials['cookie']['expiry_days']
)

# Display the login form and handle authentication
authenticator.login('main')

# Display the sidebar navigation only after login
if st.session_state.get("logged_in", False):
    make_sidebar()

st.title("Welcome to Employee Survey 2024 Result Dashboard")

# Handle authentication status
if st.session_state.get("authentication_status", False):
    st.session_state.logged_in = True

    # Get the unit for the logged-in user from the credentials
    username = st.session_state["username"]
    user_unit = credentials['credentials']['usernames'][username]['unit']
    
    # Welcome message and user's unit
    st.sidebar.write(f"Welcome {st.session_state['name']} from {user_unit}!")

    # Filter survey data based on the logged-in user's unit
    filtered_survey = df_survey[df_survey['unit'] == user_unit]
    
    # SECTION - SURVEY DATA
    st.header(f'Survey Data for {user_unit}', divider='rainbow')
    st.dataframe(filtered_survey.head())

elif st.session_state.get("authentication_status") is False:
    st.error("Incorrect username or password.")
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your username and password to log in.")

# If logged in, display the sidebar links and logout option
if st.session_state.get("logged_in", False):
    if st.sidebar.button("Log out", key="logout_button"):
        st.session_state.logged_in = False
        authenticator.logout('main')
        st.experimental_rerun()
