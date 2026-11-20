import streamlit as st
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="Nirbheed | Bus Planner", page_icon="🚌", layout="wide", initial_sidebar_state="collapsed")

# 2. LOAD DATA
@st.cache_data
def load_data():
    try:
        return pd.read_csv('crowding_model.csv.gz')
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.error("⚠️ crowding_model.csv not found. Please run build_model.py first!")
    st.stop()

all_stops = sorted(df['stop_name'].dropna().unique())

# 3. LIGHT/DARK THEME STATE
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Dynamic Colors
if st.session_state.theme == 'dark':
    bg_color = "#02122c" # Navy
    text_color = "#ffffff"
    accent_border = "#febb02" # Yellow
    card_bg = "rgba(255, 255, 255, 0.05)"
else:
    bg_color = "#f0f2f5" # Light Gray
    text_color = "#1a1a1a"
    accent_border = "#006ce4" # Blue
    card_bg = "#ffffff"

# 4. INJECT CSS (Theme Styles + The Bus Loader Overlay)
# 4. INJECT CSS (Theme Styles + The Bus Loader Overlay)
st.markdown(f"""
<style>
    /* 1. Fix Full Screen Background */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        transition: background-color 0.3s ease;
    }}
    [data-testid="stHeader"] {{ display: none; }}
    
    /* 2. Style the Native Form to look like Booking.com */
    [data-testid="stForm"] {{
        background-color: white !important;
        border: 4px solid {accent_border} !important;
        border-radius: 8px !important;
        padding: 10px 10px 25px 10px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
    }}
    
    /* Force text inside the white form to be dark */
    [data-testid="stForm"] p, [data-testid="stForm"] label {{
        color: #1a1a1a !important; font-weight: 700 !important;
    }}
    
    /* 3. FIX THE DROPDOWNS: Force them to be light inside the form */
    [data-testid="stForm"] div[data-baseweb="select"] > div {{
        background-color: #f0f2f5 !important;
        color: #1a1a1a !important;
        border-radius: 6px !important;
        border: 1px solid #e7e7e7 !important;
    }}
    [data-testid="stForm"] div[data-baseweb="select"] span {{
        color: #1a1a1a !important;
    }}
    
    /* 4. The Search Button */
    [data-testid="stFormSubmitButton"] > button {{
        background-color: #006ce4 !important; color: white !important;
        font-weight: 800 !important; font-size: 1.1rem !important;
        border: none !important; width: 100% !important; height: 100% !important;
        padding: 10px !important; margin-top: 15px !important;
    }}
    [data-testid="stFormSubmitButton"] > button:hover {{ background-color: #0056b3 !important; }}
    
    /* 5. THE NIRBHEED BUS LOADER */
    #nirbheed-loader {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #010a17; z-index: 999999;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        animation: fadeOutLoader 0.5s ease-in-out 2.5s forwards; 
        pointer-events: none;
    }}
    @keyframes fadeOutLoader {{ to {{ opacity: 0; visibility: hidden; }} }}
    
    .loader-circle {{
        width: 80px; height: 80px; border: 4px solid rgba(255,255,255,0.1);
        border-top: 4px solid #febb02; border-radius: 50%;
        animation: spin 1s linear infinite; position: absolute;
    }}
    .bus-icon {{ font-size: 35px; animation: drive 1s ease-in-out infinite alternate; }}
    @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
    @keyframes drive {{ 100% {{ transform: translateY(-8px); }} }}
</style>

<!-- INJECT THE HTML LOADER DIRECTLY INTO THE PAGE -->
<div id="nirbheed-loader">
    <div style="position:relative; display:flex; justify-content:center; align-items:center; width:100px; height:100px;">
        <div class="loader-circle"></div>
        <div class="bus-icon">🚌</div>
    </div>
    <h2 style="color:white; margin-top:20px; letter-spacing: 2px;">NIRBHEED</h2>
    <p style="color:#888;">Analyzing Live Delhi Crowd Data...</p>
</div>
""", unsafe_allow_html=True)


# 5. HEADER & THEME TOGGLE
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown(f"<h2 style='color: #febb02; margin-top: 10px;'>🚌 Nirbheed</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-weight:800; font-size: 3.5rem; margin-bottom: 0; line-height: 1.1; background: linear-gradient(90deg, #006ce4, #8b5cf6, #febb02); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Smart journeys.<br>No crowded surprises.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a0aec0; font-size: 1.2rem; margin-bottom: 30px;'>Compare Delhi bus routes by travel time and live seating capacity.</p>", unsafe_allow_html=True)
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    mode_text = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
    st.button(mode_text, on_click=toggle_theme, use_container_width=True)

# 6. THE NATIVE SEARCH BAR
with st.form("search_form"):
    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
    with c1:
        start_stop = st.selectbox("📍 Boarding At", all_stops, index=0)
    with c2:
        end_stop = st.selectbox("🏁 Destination", all_stops, index=len(all_stops)-1 if len(all_stops) > 0 else 0)
    with c3:
        hour_selected = st.selectbox("🕒 Departure Time", [f"{h:02d}:00" for h in range(5, 24)], index=4)
    with c4:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        search_pressed = st.form_submit_button("Search Buses")

# 7. ROUTING LOGIC
if search_pressed:
    hour = int(hour_selected.split(":")[0])
    st.markdown("---")
    
    start_routes = set(df[df['stop_name'] == start_stop]['route'])
    end_routes = set(df[df['stop_name'] == end_stop]['route'])
    common_routes = list(start_routes.intersection(end_routes))
    
    if not common_routes:
        st.error(f"No direct routes found between {start_stop} and {end_stop} at {hour:02d}:00.", icon="🚧")
    else:
        st.success(f"✅ Found {len(common_routes)} routes for your journey.")
        for route in common_routes:
            route_hour_data = df[(df['route'] == route) & (df['hour'] == hour)].sort_values(by='stop_sequence')
            if route_hour_data.empty: continue
                
            try:
                start_idx = route_hour_data[route_hour_data['stop_name'] == start_stop].index[0]
                end_idx = route_hour_data[route_hour_data['stop_name'] == end_stop].index[0]
                segment_data = route_hour_data.loc[min(start_idx, end_idx):max(start_idx, end_idx)]
            except IndexError:
                segment_data = route_hour_data
            
            max_load = segment_data['current_load'].max()
            travel_time = max(len(segment_data) * 2, 15) 
            
            if max_load < 35:
                status, color, progress_val = "🟢 Seats Available", "#22C55E", min(max_load / 70.0, 1.0)
            elif max_load <= 60:
                status, color, progress_val = "🟡 Standing Room", "#EAB308", min(max_load / 70.0, 1.0)
            else:
                status, color, progress_val = "🔴 Crowded", "#EF4444", 1.0

            with st.container(border=True):
                head1, head2 = st.columns([2, 1])
                with head1: st.markdown(f"<h3 style='margin: 0; color: {text_color};'>Route {route}</h3>", unsafe_allow_html=True)
                with head2: 
                    st.markdown(f"<div style='text-align: right; font-weight: bold; color: {color};'>{status}</div>", unsafe_allow_html=True)
                    st.progress(progress_val)
                
                st.divider()
                m1, m2, m3 = st.columns(3)
                m1.metric("Travel Time", f"{travel_time} mins")
                m2.metric("Peak Load", f"{int(max_load)} pax")
                m3.metric("Stops", len(segment_data))
