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
    st.error("⚠️ crowding_model.csv.gz not found. Please run build_model.py first!")
    st.stop()

# Get unique sorted lists for dropdowns
all_stops = sorted(df['stop_name'].dropna().unique())
all_routes = sorted(df['route'].dropna().astype(str).unique())
hours_list = [f"{h:02d}:00" for h in range(0, 24)]

# 3. INJECT CSS (Corrected Background Layering with User's URL)
st.markdown("""
<style>
    /* 1. Make inner containers transparent so the background shows through */
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"] {
        background: transparent !important;
        background-color: transparent !important;
    }

    /* 2. Apply the animated background strictly to the OUTER layer */
    .stApp {
        background-image: linear-gradient(rgba(6, 15, 30, 0.75), rgba(6, 15, 30, 0.75)), 
                          url("https://i.pinimg.com/736x/4e/f6/45/4ef6459bdb675a8d8e34158ae4bb5233.jpg") !important;
        background-size: cover !important;
        background-position: 0% 50% !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
        animation: smooth-drive 45s linear infinite alternate !important;
    }
    
    /* 3. Subtle, slow panning motion to simulate a moving bus */
    @keyframes smooth-drive {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
    
    /* 4. Style the Forms */
    [data-testid="stForm"] {
        background-color: rgba(10, 15, 25, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6) !important;
    }
    
    /* Force form text to be light for the dark theme */
    [data-testid="stForm"] label, [data-testid="stForm"] p {
        color: #e2e8f0 !important;
    }
    
    /* 5. The Search Buttons */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #febb02 !important; 
        color: #02122c !important;
        font-weight: 800 !important; 
        font-size: 1.1rem !important;
        border: none !important; 
        width: 100% !important; 
        height: 100% !important;
        padding: 10px !important; 
        margin-top: 15px !important;
        border-radius: 8px !important;
        transition: transform 0.2s ease, background-color 0.2s ease;
    }
    [data-testid="stFormSubmitButton"] > button:hover { 
        transform: scale(1.02);
        background-color: #e5a800 !important; 
    }
    
    /* 6. Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: rgba(255,255,255,0.6);
        font-weight: 600;
        font-size: 1.2rem;
    }
    .stTabs [aria-selected="true"] {
        color: #febb02 !important;
        border-bottom: 3px solid #febb02 !important;
    }
    
    /* 7. The Nirbheed Loader Animation */
    #nirbheed-loader {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #060f1e; z-index: 999999;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        animation: fadeOutLoader 0.6s ease-in-out 2.5s forwards; 
        pointer-events: none;
    }
    @keyframes fadeOutLoader { to { opacity: 0; visibility: hidden; } }
    
    .loader-circle {
        width: 80px; height: 80px; border: 4px solid rgba(255,255,255,0.05);
        border-top: 4px solid #febb02; border-radius: 50%;
        animation: spin 1.2s linear infinite; position: absolute;
    }
    .bus-icon { font-size: 35px; animation: drive 1.5s ease-in-out infinite alternate; z-index: 2;}
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes drive { 100% { transform: translateY(-6px); } }
</style>

<!-- LOADER HTML -->
<div id="nirbheed-loader">
    <div style="position:relative; display:flex; justify-content:center; align-items:center; width:100px; height:100px;">
        <div class="loader-circle"></div>
        <div class="bus-icon">🚌</div>
    </div>
    <h2 style="color:white; margin-top:20px; letter-spacing: 2px;">NIRBHEED</h2>
    <p style="color:#888;">Mapping Live Delhi Transit...</p>
</div>
""", unsafe_allow_html=True)

# 4. HEADER
st.markdown(f"<h2 style='color: #febb02; margin-top: 10px;'>🚌 Nirbheed</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='font-weight:800; font-size: 3.5rem; margin-bottom: 0; line-height: 1.1; color: white;'>Smart journeys.<br>No crowded surprises.</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #cbd5e1; font-size: 1.2rem; margin-bottom: 30px;'>Compare Delhi bus routes by travel time and live seating capacity.</p>", unsafe_allow_html=True)

# 5. TABS FOR SEARCH OPTIONS
tab1, tab2 = st.tabs(["📍 Search by Stops", "🚌 Search by Route"])

# ==========================================
# TAB 1: SEARCH BY STOPS
# ==========================================
with tab1:
    with st.form("search_form_stops"):
        c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
        with c1:
            start_stop = st.selectbox("📍 Boarding At", all_stops, index=None, placeholder="Search Origin...")
        with c2:
            end_stop = st.selectbox("🏁 Destination", all_stops, index=None, placeholder="Search Destination...")
        with c3:
            hour_stops = st.selectbox("🕒 Departure Time", hours_list, index=9, key="hour_stops")
        with c4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            search_stops_pressed = st.form_submit_button("Find Buses")

# ==========================================
# TAB 2: SEARCH BY ROUTE
# ==========================================
with tab2:
    with st.form("search_form_route"):
        c1, c2, c3 = st.columns([4, 2, 2])
        with c1:
            selected_route = st.selectbox("🚌 Select Bus Route", all_routes, index=None, placeholder="Search for a Route (e.g. 102UP)")
        with c2:
            hour_route = st.selectbox("🕒 Departure Time", hours_list, index=9, key="hour_route")
        with c3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            search_route_pressed = st.form_submit_button("Check Crowding")

# 6. SHARED UI HELPER FUNCTION
def display_route_card(route, status, max_load, travel_time, stops_count, origin, destination):
    if status == "🟢 Seats Available":
        color, progress_val = "#22C55E", min(max_load / 70.0, 1.0)
    elif status == "🟡 Standing Room":
        color, progress_val = "#EAB308", min(max_load / 70.0, 1.0)
    else:
        color, progress_val = "#EF4444", 1.0

    with st.container():
        st.markdown(f"""
        <div style="background-color: rgba(20, 25, 35, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; margin-bottom: 15px; backdrop-filter: blur(8px);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 2;">
                    <h3 style='margin: 0; color: white;'>Route {route}</h3>
                    <p style='color: #94a3b8; font-size: 0.9rem; margin-top: 5px; line-height: 1.3;'>{origin} ➔ {destination}</p>
                </div>
                <div style="flex: 1; text-align: right;">
                    <div style='font-weight: bold; font-size: 1.1rem; color: {color}; margin-bottom: 5px;'>{status}</div>
                </div>
            </div>
            <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; margin-top: 10px; margin-bottom: 15px;">
                <div style="width: {progress_val * 100}%; background-color: {color}; height: 100%; border-radius: 4px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;">
                <div style="text-align: center; flex: 1;">
                    <div style="color: #94a3b8; font-size: 0.8rem;">Travel Time</div>
                    <div style="color: white; font-weight: bold; font-size: 1.1rem;">{travel_time} mins</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="color: #94a3b8; font-size: 0.8rem;">Peak Load</div>
                    <div style="color: white; font-weight: bold; font-size: 1.1rem;">{int(max_load)} pax</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="color: #94a3b8; font-size: 0.8rem;">Stops</div>
                    <div style="color: white; font-weight: bold; font-size: 1.1rem;">{stops_count}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
# ==========================================
# 8. ROUTING LOGIC EXECUTION
# ==========================================

# LOGIC FOR TAB 1 (Stops)
if search_stops_pressed:
    if not start_stop or not end_stop:
        st.error("⚠️ Please select both a Boarding point and a Destination.")
    else:
        hour = int(hour_stops.split(":")[0])
        st.markdown("---")
        
        # 1. FORCE NUMERIC SEQUENCES (Fixes the '10' < '2' string bug)
        df['stop_sequence'] = pd.to_numeric(df['stop_sequence'], errors='coerce')
        
        # 2. Get unique routes for start and end
        start_matches = df[df['stop_name'] == start_stop][['route', 'stop_sequence']].dropna().drop_duplicates()
        end_matches = df[df['stop_name'] == end_stop][['route', 'stop_sequence']].dropna().drop_duplicates()
        
        possible_routes = pd.merge(start_matches, end_matches, on='route', suffixes=('_start', '_end'))
        
        if possible_routes.empty:
            st.error(f"🚧 No direct routes connect {start_stop} and {end_stop}.")
        else:
            # 3. Check Sequence (Must logically go from a lower sequence to a higher sequence)
            valid_paths = possible_routes[possible_routes['stop_sequence_start'] < possible_routes['stop_sequence_end']]
            
            if valid_paths.empty:
                st.error("🔄 The bus travels the opposite direction! Try swapping Boarding and Destination.")
            else:
                displayed_count = 0
                valid_route_names = valid_paths['route'].unique()
                
                for route in valid_route_names:
                    # Filter for this exact hour
                    route_hour_data = df[(df['route'] == route) & (df['hour'] == hour)]
                    
                    if not route_hour_data.empty:
                        # Find the bounds for this specific route slice
                        seq_start = valid_paths[valid_paths['route'] == route]['stop_sequence_start'].min()
                        seq_end = valid_paths[valid_paths['route'] == route]['stop_sequence_end'].max()
                        
                        segment_data = route_hour_data[(route_hour_data['stop_sequence'] >= seq_start) & (route_hour_data['stop_sequence'] <= seq_end)]
                        
                        if not segment_data.empty:
                            displayed_count += 1
                            max_load = segment_data['current_load'].max()
                            travel_time = max(len(segment_data) * 2, 15)
                            
                            if max_load < 35: status = "🟢 Seats Available"
                            elif max_load <= 60: status = "🟡 Standing Room"
                            else: status = "🔴 Crowded"

                            display_route_card(route, status, max_load, travel_time, len(segment_data), start_stop, end_stop)
                
                if displayed_count == 0:
                    st.warning(f"🚏 The route exists, but we have no active bus load data for {hour:02d}:00.")
                else:
                    st.success(f"✅ Found {displayed_count} active route option(s) for your journey.")

# LOGIC FOR TAB 2 (Route)
if search_route_pressed:
    if not selected_route:
        st.error("⚠️ Please select a route from the dropdown.")
    else:
        hour = int(hour_route.split(":")[0])
        st.markdown("---")
        
        # 1. FORCE NUMERIC SEQUENCES
        df['stop_sequence'] = pd.to_numeric(df['stop_sequence'], errors='coerce')
        
        # Fetch data, filter for hour, deduplicate and sort
        route_data = df[(df['route'] == selected_route) & (df['hour'] == hour)].drop_duplicates(subset=['stop_sequence']).sort_values(by='stop_sequence')
        
        if route_data.empty:
            st.warning(f"🚏 No active bus load data recorded for Route {selected_route} at {hour:02d}:00.")
        else:
            st.success(f"✅ Displaying live crowding for Route {selected_route}.")
            
            start_stop_str = route_data.iloc[0]['stop_name']
            end_stop_str = route_data.iloc[-1]['stop_name']
            max_load = route_data['current_load'].max()
            travel_time = max(len(route_data) * 2, 15)
            
            if max_load < 35: status = "🟢 Seats Available"
            elif max_load <= 60: status = "🟡 Standing Room"
            else: status = "🔴 Crowded"

            display_route_card(selected_route, status, max_load, travel_time, len(route_data), start_stop_str, end_stop_str)
