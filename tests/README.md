# Food Rescue WebSocket Tests

This folder contains test scripts for validating the WebSocket functionality of the Food Rescue system.

## Test Files

### 1. `websocket_tester.py` - Interactive WebSocket Tester
**Main testing tool with multiple modes**

#### Usage:
```bash
# Full test suite (recommended)
python tests/websocket_tester.py

# Ping test only
python tests/websocket_tester.py --mode ping

# Donation notification test
python tests/websocket_tester.py --mode donation

# Interactive mode for manual testing
python tests/websocket_tester.py --mode interactive
```

#### Interactive Commands:
- `ping` - Test ping/pong functionality
- `donation` - Create test donation and verify notification
- `listen` - Listen for incoming messages
- `stats` - Get WebSocket connection statistics
- `custom:<type>:<data>` - Send custom message
- `quit` - Exit interactive mode

### 2. `test_integrated_websocket.py` - Full Integration Test
**Comprehensive test that validates end-to-end functionality**

```bash
python tests/test_integrated_websocket.py
```

Tests:
- WebSocket connection
- Ping/pong communication
- Real-time donation notifications
- API integration

### 3. `test_websocket.py` - Basic WebSocket Test
**Simple connection and message test**

```bash
python tests/test_websocket.py
```

### 4. `test_http.py` - HTTP API Test
**Tests the REST API endpoints**

```bash
python tests/test_http.py
```

## Prerequisites

Make sure the server is running:
```bash
python main.py
```

And ensure these packages are installed:
```bash
pip install requests websockets
```

## Example Test Session

```bash
# 1. Start the server (in another terminal)
python main.py

# 2. Run the interactive tester
python tests/websocket_tester.py --mode interactive

# 3. Try these commands:
ping
donation
stats
listen
quit
```

## Expected Results

✅ **Successful test output:**
- WebSocket connects without errors
- Ping receives pong response
- Creating donation triggers real-time notification
- Multiple clients can connect simultaneously

❌ **Common issues:**
- Server not running: Start `python main.py`
- Port conflicts: Check if port 8000 is available
- Missing dependencies: Install `requests` and `websockets`

## WebSocket Endpoints

- `ws://127.0.0.1:8000/ws` - General connection
- `ws://127.0.0.1:8000/ws/ngo/{ngo_id}` - NGO-specific
- `ws://127.0.0.1:8000/ws/donor` - Donor-specific

## API Endpoints Tested

- `POST /api/donations/` - Create donation (triggers WebSocket)
- `GET /api/ws/stats` - WebSocket connection statistics
- `POST /api/pickups/` - Create pickup (triggers WebSocket)
- `PATCH /pickups/{id}` - Update pickup status (triggers WebSocket)