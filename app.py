import socketio
import eventlet
from flask import Flask, send_from_directory

# The SocketIO server is initialized with CORS settings to allow connections from any origin
sio = socketio.Server(cors_allowed_origins='*')

# The standard Flask application
app = Flask(__name__)

# A dictionary to store active pickups and their latest locations
active_pickups = {}

@app.route('/')
def index():
    return "Real-time tracking server is running!"

@app.route('/donor.html')
def serve_donor_page():
    return send_from_directory('.', 'donor.html')

@app.route('/ngo.html')
def serve_ngo_page():
    return send_from_directory('.', 'ngo.html')

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def join_pickup(sid, data):
    pickup_id = data.get('pickupId')
    sio.enter_room(sid, pickup_id)
    print(f'Client {sid} joined room {pickup_id}')
    
    if pickup_id in active_pickups:
        sio.emit('location_update', active_pickups[pickup_id], room=sid)

@sio.event
def location_update(sid, data):
    pickup_id = data.get('pickupId')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if pickup_id and latitude and longitude:
        active_pickups[pickup_id] = {'latitude': latitude, 'longitude': longitude}
        sio.emit('location_update', data, room=pickup_id, skip_sid=sid)
        print(f"Broadcasted location for {pickup_id}: {latitude}, {longitude}")

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    app = socketio.WSGIApp(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 3000)), app)