#!/usr/bin/env python3
"""
Food Rescue Database Web Dashboard
Creates a live HTML dashboard that auto-updates with database changes
"""

import sqlite3
import json
import time
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import webbrowser
from urllib.parse import urlparse, parse_qs

class DatabaseWebServer:
    def __init__(self, db_path="food_rescue.db", port=8080):
        self.db_path = db_path
        self.port = port
        self.server = None
        
    def get_database_data(self):
        """Get all database data as JSON"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            
            # Get donations
            cursor.execute("SELECT * FROM donations ORDER BY id DESC")
            donations = [dict(row) for row in cursor.fetchall()]
            
            # Get NGOs
            cursor.execute("SELECT * FROM ngos ORDER BY id")
            ngos = [dict(row) for row in cursor.fetchall()]
            
            # Get pickups
            cursor.execute("SELECT * FROM pickups ORDER BY id DESC")
            pickups = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            # Calculate statistics
            total_donations = len(donations)
            available_donations = len([d for d in donations if d.get('status') == 'available'])
            delivered_donations = len([d for d in donations if d.get('status') == 'delivered'])
            accepted_donations = len([d for d in donations if d.get('status') == 'accepted'])
            
            return {
                'donations': donations,
                'ngos': ngos,
                'pickups': pickups,
                'stats': {
                    'total_donations': total_donations,
                    'available_donations': available_donations,
                    'delivered_donations': delivered_donations,
                    'accepted_donations': accepted_donations,
                    'total_ngos': len(ngos),
                    'total_pickups': len(pickups),
                    'last_updated': datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {'error': str(e)}

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_dashboard()
        elif parsed_path.path == '/api/data':
            self.serve_api_data()
        elif parsed_path.path == '/favicon.ico':
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/clear-database':
            self.clear_database()
        else:
            self.send_response(404)
            self.end_headers()
    
    def clear_database(self):
        """Clear all data from database tables while preserving schema"""
        try:
            conn = sqlite3.connect(self.server.db_path)
            cursor = conn.cursor()
            
            # Delete all data but preserve schema
            cursor.execute("DELETE FROM pickups")
            cursor.execute("DELETE FROM donations") 
            cursor.execute("DELETE FROM ngos")
            
            # Reset auto-increment counters
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('donations', 'ngos', 'pickups')")
            
            conn.commit()
            conn.close()
            
            # Return success response
            response = json.dumps({'success': True, 'message': 'Database cleared successfully'})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(response.encode())))
            self.end_headers()
            self.wfile.write(response.encode())
            
        except Exception as e:
            # Return error response
            response = json.dumps({'success': False, 'error': str(e)})
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(response.encode())))
            self.end_headers()
            self.wfile.write(response.encode())
    
    def serve_dashboard(self):
        """Serve the main HTML dashboard"""
        html_content = self.generate_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(html_content.encode())))
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_api_data(self):
        """Serve database data as JSON API"""
        db_server = DatabaseWebServer(self.server.db_path)
        data = db_server.get_database_data()
        
        json_data = json.dumps(data, default=str)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(json_data.encode())))
        self.end_headers()
        self.wfile.write(json_data.encode())
    
    def generate_dashboard_html(self):
        """Generate the complete HTML dashboard"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍽️ Food Rescue Database Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .status-bar {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: white;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        
        .data-section {
            background: white;
            margin-bottom: 30px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .section-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: bold;
        }
        
        .table-container {
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        .status {
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status.available { background: #d4edda; color: #155724; }
        .status.accepted { background: #fff3cd; color: #856404; }
        .status.delivered { background: #d1ecf1; color: #0c5460; }
        .status.picked_up { background: #f8d7da; color: #721c24; }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .refresh-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 10px 15px;
            border-radius: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        
        .pulse {
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .food-types {
            font-size: 0.9em;
            color: #666;
        }
        
        .clear-button {
            background: linear-gradient(135deg, #ff6b6b, #ee5a5a);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
            transition: all 0.3s ease;
            margin: 10px;
        }
        
        .clear-button:hover {
            background: linear-gradient(135deg, #ff5252, #d32f2f);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
        }
        
        .clear-button:active {
            transform: translateY(0);
        }
        
        .button-container {
            text-align: center;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽️ Food Rescue Database Dashboard</h1>
            <p>Real-time monitoring of donations, NGOs, and pickups</p>
            
            <div class="button-container">
                <button class="clear-button" onclick="clearDatabase()">
                    🗑️ Clear Database
                </button>
            </div>
        </div>
        
        <div class="refresh-indicator" id="refreshIndicator">
            🔄 Auto-refreshing...
        </div>
        
        <div class="status-bar" id="statusBar">
            <span id="lastUpdated">Loading...</span>
        </div>
        
        <div class="stats-grid" id="statsGrid">
            <!-- Stats will be populated by JavaScript -->
        </div>
        
        <div class="data-section">
            <div class="section-header">📦 Donations</div>
            <div class="table-container">
                <div id="donationsLoading" class="loading">Loading donations...</div>
                <table id="donationsTable" style="display: none;">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Restaurant</th>
                            <th>Food Description</th>
                            <th>Quantity</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Expires</th>
                        </tr>
                    </thead>
                    <tbody id="donationsBody">
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="data-section">
            <div class="section-header">🏢 NGOs</div>
            <div class="table-container">
                <div id="ngosLoading" class="loading">Loading NGOs...</div>
                <table id="ngosTable" style="display: none;">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Phone</th>
                            <th>Capacity</th>
                            <th>Food Types</th>
                            <th>Schedule</th>
                        </tr>
                    </thead>
                    <tbody id="ngosBody">
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="data-section">
            <div class="section-header">🚚 Pickups</div>
            <div class="table-container">
                <div id="pickupsLoading" class="loading">Loading pickups...</div>
                <table id="pickupsTable" style="display: none;">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Donation ID</th>
                            <th>NGO ID</th>
                            <th>Pickup Time</th>
                            <th>Delivery Time</th>
                            <th>Beneficiaries</th>
                        </tr>
                    </thead>
                    <tbody id="pickupsBody">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let lastDataHash = '';
        
        function formatDateTime(dateStr) {
            if (!dateStr) return 'Not set';
            try {
                const date = new Date(dateStr);
                return date.toLocaleString();
            } catch {
                return dateStr;
            }
        }
        
        function formatFoodTypes(foodTypesStr) {
            if (!foodTypesStr) return '[]';
            try {
                const types = JSON.parse(foodTypesStr);
                if (Array.isArray(types)) {
                    return types.join(', ');
                }
                return foodTypesStr;
            } catch {
                return foodTypesStr;
            }
        }
        
        function updateStats(stats) {
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${stats.total_donations || 0}</div>
                    <div class="stat-label">Total Donations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.available_donations || 0}</div>
                    <div class="stat-label">Available</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.delivered_donations || 0}</div>
                    <div class="stat-label">Delivered</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.total_ngos || 0}</div>
                    <div class="stat-label">NGOs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.total_pickups || 0}</div>
                    <div class="stat-label">Pickups</div>
                </div>
            `;
        }
        
        function updateDonations(donations) {
            const tbody = document.getElementById('donationsBody');
            const table = document.getElementById('donationsTable');
            const loading = document.getElementById('donationsLoading');
            
            tbody.innerHTML = donations.map(donation => `
                <tr>
                    <td>${donation.id}</td>
                    <td>${donation.restaurant_name || 'Unknown'}</td>
                    <td>${donation.food_description || 'No description'}</td>
                    <td>${donation.quantity || 0}</td>
                    <td><span class="status ${donation.status || 'unknown'}">${donation.status || 'unknown'}</span></td>
                    <td>${formatDateTime(donation.created_at)}</td>
                    <td>${formatDateTime(donation.expires_at)}</td>
                </tr>
            `).join('');
            
            loading.style.display = 'none';
            table.style.display = 'table';
        }
        
        function updateNGOs(ngos) {
            const tbody = document.getElementById('ngosBody');
            const table = document.getElementById('ngosTable');
            const loading = document.getElementById('ngosLoading');
            
            tbody.innerHTML = ngos.map(ngo => `
                <tr>
                    <td>${ngo.id}</td>
                    <td>${ngo.name || 'Unknown'}</td>
                    <td>${ngo.contact_phone || 'No phone'}</td>
                    <td>${ngo.storage_capacity || 0}</td>
                    <td class="food-types">${formatFoodTypes(ngo.accepted_food_types)}</td>
                    <td>${ngo.operating_schedule || '24/7'}</td>
                </tr>
            `).join('');
            
            loading.style.display = 'none';
            table.style.display = 'table';
        }
        
        function updatePickups(pickups) {
            const tbody = document.getElementById('pickupsBody');
            const table = document.getElementById('pickupsTable');
            const loading = document.getElementById('pickupsLoading');
            
            tbody.innerHTML = pickups.map(pickup => `
                <tr>
                    <td>${pickup.id}</td>
                    <td>${pickup.donation_id}</td>
                    <td>${pickup.ngo_id}</td>
                    <td>${formatDateTime(pickup.pickup_time)}</td>
                    <td>${formatDateTime(pickup.delivery_time)}</td>
                    <td>${pickup.beneficiaries_count || 0}</td>
                </tr>
            `).join('');
            
            loading.style.display = 'none';
            table.style.display = 'table';
        }
        
        function showError(message) {
            const container = document.querySelector('.container');
            container.innerHTML = `
                <div class="header">
                    <h1>🍽️ Food Rescue Database Dashboard</h1>
                </div>
                <div class="error">
                    <strong>Error:</strong> ${message}
                </div>
            `;
        }
        
        async function clearDatabase() {
            if (!confirm('⚠️ Are you sure you want to clear the entire database?\\n\\nThis will delete ALL donations, NGOs, and pickups data.\\nThis action cannot be undone!')) {
                return;
            }
            
            try {
                document.getElementById('refreshIndicator').innerHTML = '🧹 Clearing database...';
                document.getElementById('refreshIndicator').classList.add('pulse');
                
                const response = await fetch('/api/clear-database', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('✅ Database cleared successfully!\\n\\nAll data has been removed and auto-increment counters have been reset.');
                    // Refresh the data immediately
                    await fetchData();
                } else {
                    alert(`❌ Failed to clear database: ${result.error}`);
                }
                
            } catch (error) {
                alert(`❌ Error clearing database: ${error.message}`);
            } finally {
                document.getElementById('refreshIndicator').innerHTML = '🔄 Auto-refreshing...';
                document.getElementById('refreshIndicator').classList.remove('pulse');
            }
        }
        
        async function fetchData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                // Check if data changed
                const dataHash = JSON.stringify(data);
                if (dataHash !== lastDataHash) {
                    lastDataHash = dataHash;
                    
                    // Flash the refresh indicator
                    const indicator = document.getElementById('refreshIndicator');
                    indicator.classList.add('pulse');
                    setTimeout(() => indicator.classList.remove('pulse'), 1000);
                }
                
                // Update UI
                updateStats(data.stats);
                updateDonations(data.donations);
                updateNGOs(data.ngos);
                updatePickups(data.pickups);
                
                // Update status bar
                document.getElementById('lastUpdated').textContent = 
                    `Last updated: ${new Date().toLocaleTimeString()}`;
                
            } catch (error) {
                showError(`Failed to fetch data: ${error.message}`);
            }
        }
        
        // Initial load
        fetchData();
        
        // Auto-refresh every 3 seconds
        setInterval(fetchData, 3000);
    </script>
</body>
</html>
        '''

def start_dashboard_server(db_path="food_rescue.db", port=8080):
    """Start the web dashboard server"""
    
    class CustomHTTPServer(HTTPServer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.db_path = db_path
    
    server_address = ('', port)
    httpd = CustomHTTPServer(server_address, DashboardHandler)
    httpd.db_path = db_path
    
    print(f"🌐 Food Rescue Dashboard Server starting on port {port}")
    print(f"📊 Dashboard URL: http://localhost:{port}")
    print(f"🔍 Monitoring database: {db_path}")
    print("🔄 Auto-refresh: Every 3 seconds")
    print("\n🚀 Opening dashboard in browser...")
    
    # Open browser automatically
    def open_browser():
        time.sleep(1)  # Wait for server to start
        webbrowser.open(f'http://localhost:{port}')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⏹️  Dashboard server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Food Rescue Web Dashboard")
    parser.add_argument("--db", default="food_rescue.db", help="Database file path")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    
    args = parser.parse_args()
    
    start_dashboard_server(args.db, args.port)