# Nirbheed - Delhi Smart Transit Planner  
Built for the Delhi Transport Stack Hackathon (Phase 1), Nirbheed helps commuters avoid crowded buses. By processing over 2.5 million ETM ticketing records and cross-referencing them with static GTFS network schedules, this tool predicts stop-by-stop bus capacity and offers commuters routes optimized for both speed and comfort.  


[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)] (https://nirbheed-by-kammari-sushma.streamlit.app/)  
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)  
[![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458.svg)](https://pandas.pydata.org/)  
[![Hackathon](https://img.shields.io/badge/Delhi_Transport_Stack-Problem_2-febb02.svg)](https://delhi.transportstack.in/hackathon/#ps2)  

**A smart journey planner for Delhi commuters that ranks routes by real-time crowding estimates, not just travel time.** Built for Phase 1 of the Delhi Transport Stack Hackathon.  

### 🔗 [Live Demo: Test the Nirbheed App Here](https://nirbheed-by-kammari-sushma.streamlit.app/)  

*(Note: If the app has gone to sleep, click "Wake Up" and give it a few seconds to load the compressed GTFS model).*  

---  

## 🎯 The Challenge & Our Solution  
Commuters in Delhi often skip crowded buses even if they are faster, yet traditional planners only show time. **Nirbheed** bridges this gap. We ingested **2.56 million ETM transactional records** and mapped them against **static GTFS schedules** to create a highly accurate, hourly-aggregated crowding model.   

### Key Innovations  
1. **Segment-Specific Load:** Instead of showing the average crowding of a whole route, Nirbheed calculates the maximum passenger load *specifically for the exact segment* the commuter intends to travel.  
2. **The "Invisible Rider" Adjustment:** Raw ETM data misses monthly pass holders. Our ETL pipeline applies a mathematical heuristic (a 20% multiplier) to boardings and alightings to represent true physical bus loads.  
3. **Cognitive-Load UI:** Commuters shouldn't have to read raw data. We translate complex running loads into three instant visual categories based on Delhi's 12m bus capacities:  
   - 🟢 **Seats Available** (Load < 35)  
   - 🟡 **Standing Room** (35 ≤ Load ≤ 60)  
   - 🔴 **Crowded** (Load > 60)  

---  

## 🏗️ System Architecture  

Our solution strictly decouples heavy data processing from the user interface to ensure a lightning-fast web app.  

```text  
[Raw ETM Data (2.5M+ rows)] + [Static GTFS (Stops/Routes)]  
           ↓  
⚙️ build_model.py (Offline ETL Pipeline)  
           ├─ 1. Hourly time-window aggregation  
           ├─ 2. GTFS stop-sequence sorting (fixes alphabetical drift)  
           ├─ 3. Running load calculation ($Load = Boardings - Alightings$)  
           └─ 4. Pass-holder multipliers applied  
           ↓  
💾 crowding_model.csv.gz (Compressed output)  
           ↓  
🖥️ app.py (Streamlit UI)  
           └─ User inputs Origin/Destination/Time -> Instant visual routing  
