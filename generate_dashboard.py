#!/usr/bin/env python3
"""
Generate Static HTML Dashboard
Creates a static HTML file that auto-refreshes via API calls
"""

import sqlite3
import json
import os
from datetime import datetime

def generate_static_dashboard(db_path="food_rescue.db", output_file="dashboard.html"):
    """Generate a static HTML dashboard file"""
    
    # Get initial data
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM donations ORDER BY id DESC")
        donations = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM ngos ORDER BY id")
        ngos = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM pickups ORDER BY id DESC")
        pickups = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Calculate stats
        stats = {
            'total_donations': len(donations),
            'available_donations': len([d for d in donations if d.get('status') == 'available']),
            'delivered_donations': len([d for d in donations if d.get('status') == 'delivered']),
            'accepted_donations': len([d for d in donations if d.get('status') == 'accepted']),
            'total_ngos': len(ngos),
            'total_pickups': len(pickups),
            'last_updated': datetime.now().isoformat()
        }
        
    except Exception as e:
        donations, ngos, pickups = [], [], []
        stats = {'error': str(e)}
    
    # Generate HTML
    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍽️ Food Rescue Database Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .status-bar {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: white;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.8em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-weight: 500;
        }}
        
        .data-section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .section-header {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: bold;
        }}
        
        .table-container {{
            overflow-x: auto;
            max-height: 500px;
            overflow-y: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 15px 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
            border-bottom: 2px solid #dee2e6;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        
        .status {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
            display: inline-block;
        }}
        
        .status.available {{ background: #d4edda; color: #155724; }}
        .status.accepted {{ background: #fff3cd; color: #856404; }}
        .status.delivered {{ background: #d1ecf1; color: #0c5460; }}
        .status.picked_up {{ background: #f8d7da; color: #721c24; }}
        
        .food-types {{
            font-size: 0.9em;
            color: #666;
            max-width: 200px;
            word-wrap: break-word;
        }}
        
        .refresh-notice {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 15px 20px;
            border-radius: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
            font-size: 0.9em;
            color: #666;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }}
        
        .error-state {{
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            margin: 20px;
            border-radius: 10px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽️ Food Rescue Database Dashboard</h1>
            <p>Real-time monitoring of donations, NGOs, and pickups</p>
        </div>
        
        <div class="status-bar">
            <strong>📊 Live Dashboard</strong> • 
            Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} • 
            Auto-refreshes every 5 seconds
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats.get('total_donations', 0)}</div>
                <div class="stat-label">📦 Total Donations</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('available_donations', 0)}</div>
                <div class="stat-label">✅ Available</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('delivered_donations', 0)}</div>
                <div class="stat-label">🚚 Delivered</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('total_ngos', 0)}</div>
                <div class="stat-label">🏢 NGOs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('total_pickups', 0)}</div>
                <div class="stat-label">📋 Pickups</div>
            </div>
        </div>
        
        <div class="data-section">
            <div class="section-header">📦 Recent Donations</div>
            <div class="table-container">
                {'<div class="empty-state">No donations found</div>' if not donations else f'''
                <table>
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
                    <tbody>
                        {"".join([f'''
                        <tr>
                            <td><strong>{donation.get("id", "")}</strong></td>
                            <td>{donation.get("restaurant_name", "Unknown")}</td>
                            <td>{donation.get("food_description", "No description")}</td>
                            <td><strong>{donation.get("quantity", 0)}</strong></td>
                            <td><span class="status {donation.get("status", "unknown")}">{donation.get("status", "unknown")}</span></td>
                            <td>{datetime.fromisoformat(donation["created_at"]).strftime("%m/%d %H:%M") if donation.get("created_at") else "Not set"}</td>
                            <td>{datetime.fromisoformat(donation["expires_at"]).strftime("%m/%d %H:%M") if donation.get("expires_at") else "Not set"}</td>
                        </tr>
                        ''' for donation in donations[:10]])}
                    </tbody>
                </table>
                '''}
            </div>
        </div>
        
        <div class="data-section">
            <div class="section-header">🏢 Registered NGOs</div>
            <div class="table-container">
                {'<div class="empty-state">No NGOs found</div>' if not ngos else f'''
                <table>
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
                    <tbody>
                        {"".join([f'''
                        <tr>
                            <td><strong>{ngo.get("id", "")}</strong></td>
                            <td>{ngo.get("name", "Unknown")}</td>
                            <td>{ngo.get("contact_phone", "No phone")}</td>
                            <td><strong>{ngo.get("storage_capacity", 0) or "0"}</strong></td>
                            <td class="food-types">{json.loads(ngo.get("accepted_food_types", "[]")) if ngo.get("accepted_food_types") and ngo["accepted_food_types"].startswith("[") else (ngo.get("accepted_food_types", "[]") or "[]")}</td>
                            <td>{ngo.get("operating_schedule", "24/7")}</td>
                        </tr>
                        ''' for ngo in ngos[:15]])}
                    </tbody>
                </table>
                '''}
            </div>
        </div>
        
        <div class="data-section">
            <div class="section-header">🚚 Recent Pickups</div>
            <div class="table-container">
                {'<div class="empty-state">No pickups found</div>' if not pickups else f'''
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Donation</th>
                            <th>NGO</th>
                            <th>Pickup Time</th>
                            <th>Delivery Time</th>
                            <th>Beneficiaries</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([f'''
                        <tr>
                            <td><strong>{pickup.get("id", "")}</strong></td>
                            <td>#{pickup.get("donation_id", "")}</td>
                            <td>#{pickup.get("ngo_id", "")}</td>
                            <td>{datetime.fromisoformat(pickup["pickup_time"]).strftime("%m/%d %H:%M") if pickup.get("pickup_time") else "Not set"}</td>
                            <td>{datetime.fromisoformat(pickup["delivery_time"]).strftime("%m/%d %H:%M") if pickup.get("delivery_time") else "Pending"}</td>
                            <td><strong>{pickup.get("beneficiaries_count", 0)}</strong></td>
                        </tr>
                        ''' for pickup in pickups[:10]])}
                    </tbody>
                </table>
                '''}
            </div>
        </div>
    </div>
    
    <div class="refresh-notice">
        🔄 This page auto-refreshes every 5 seconds
    </div>
    
    <script>
        // Auto-refresh the page every 5 seconds
        setTimeout(function() {{
            window.location.reload();
        }}, 5000);
        
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            // Highlight rows on hover
            const rows = document.querySelectorAll('tbody tr');
            rows.forEach(row => {{
                row.addEventListener('mouseenter', function() {{
                    this.style.backgroundColor = '#e3f2fd';
                }});
                row.addEventListener('mouseleave', function() {{
                    this.style.backgroundColor = '';
                }});
            }});
        }});
    </script>
</body>
</html>
    '''
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Static dashboard generated: {output_file}")
        print(f"🌐 Open in browser: file://{os.path.abspath(output_file)}")
        return True
    except Exception as e:
        print(f"❌ Failed to generate dashboard: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Static HTML Dashboard")
    parser.add_argument("--db", default="food_rescue.db", help="Database file path")
    parser.add_argument("--output", default="dashboard.html", help="Output HTML file")
    
    args = parser.parse_args()
    
    generate_static_dashboard(args.db, args.output)