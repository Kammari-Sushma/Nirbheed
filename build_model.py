import pandas as pd

print("Step 1: Loading Ticket Data...")
tickets = pd.read_csv('October-Delhi.csv')
tickets['created_at'] = pd.to_datetime(tickets['created_at'], format='ISO8601')
tickets['hour'] = tickets['created_at'].dt.hour

print("Step 2: Processing Boardings & Alightings...")
boardings = tickets.groupby(['route', 'hour', 'start_stop_name'])['passenger_count'].sum().reset_index()
boardings = boardings.rename(columns={'passenger_count': 'boarded', 'start_stop_name': 'stop_name'})

valid_alights = tickets.dropna(subset=['end_stop_name'])
alightings = valid_alights.groupby(['route', 'hour', 'end_stop_name'])['passenger_count'].sum().reset_index()
alightings = alightings.rename(columns={'passenger_count': 'alighted', 'end_stop_name': 'stop_name'})

stop_activity = pd.merge(boardings, alightings, on=['route', 'hour', 'stop_name'], how='outer').fillna(0)
stop_activity['boarded'] = stop_activity['boarded'] * 1.2
stop_activity['alighted'] = stop_activity['alighted'] * 1.2
stop_activity['net_change'] = stop_activity['boarded'] - stop_activity['alighted']

print("Step 3: Integrating GTFS for correct driving order...")
# Load GTFS to get the driving sequence
routes = pd.read_csv('gtfs_data/routes.txt')
trips = pd.read_csv('gtfs_data/trips.txt')
stop_times = pd.read_csv('gtfs_data/stop_times.txt')
stops = pd.read_csv('gtfs_data/stops.txt')

# Connect the dots: route -> trip -> stop sequence -> stop name
gtfs_trips = pd.merge(trips[['route_id', 'trip_id']], routes[['route_id', 'route_short_name']], on='route_id')
gtfs_st = pd.merge(stop_times[['trip_id', 'stop_id', 'stop_sequence']], gtfs_trips, on='trip_id')
gtfs_full = pd.merge(gtfs_st, stops[['stop_id', 'stop_name']], on='stop_id')

# Create a "map" of Route + Stop Name = Sequence Number
route_sequences = gtfs_full.drop_duplicates(subset=['route_short_name', 'stop_name']).copy()
route_sequences = route_sequences[['route_short_name', 'stop_name', 'stop_sequence']]
route_sequences = route_sequences.rename(columns={'route_short_name': 'route'})

# Merge our ticket data with the GTFS map
stop_activity = pd.merge(stop_activity, route_sequences, on=['route', 'stop_name'], how='left')

# If a stop name is misspelled in ETM, push it to the end safely
stop_activity['stop_sequence'] = stop_activity['stop_sequence'].fillna(999)

print("Step 4: Calculating REAL running crowd loads...")
# THE MAGIC FIX: Sort by Route -> Hour -> Driving Order before calculating!
stop_activity = stop_activity.sort_values(by=['route', 'hour', 'stop_sequence'])

stop_activity['current_load'] = stop_activity.groupby(['route', 'hour'])['net_change'].cumsum()
stop_activity['current_load'] = stop_activity['current_load'].clip(lower=0).round().astype(int)

def get_crowd_status(load):
    if load < 35: return "🟢 Seats Available"
    elif load <= 60: return "🟡 Standing Room"
    else: return "🔴 Crowded"

stop_activity['status'] = stop_activity['current_load'].apply(get_crowd_status)

# Save the much better model
stop_activity.to_csv('crowding_model.csv.gz', index=False, compression='gzip')
print("\n--- SUCCESS! MODEL REBUILT & SAVED WITH GTFS ROUTING ---")
