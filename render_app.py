import os
import sqlite3
from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Render configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database configuration for Render (PostgreSQL or SQLite fallback)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # PostgreSQL on Render
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['USE_POSTGRESQL'] = True
else:
    # SQLite fallback
    app.config['DATABASE_PATH'] = 'rhino_dashboard.db'
    app.config['USE_POSTGRESQL'] = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

jwt = JWTManager(app)

def init_db():
    """Initialize database with sample data"""
    if app.config.get('USE_POSTGRESQL'):
        init_postgresql()
    else:
        init_sqlite()

def init_sqlite():
    """Initialize SQLite database with sample data"""
    DATABASE = app.config['DATABASE_PATH']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create incidents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            location TEXT,
            province TEXT,
            date_occurred DATE,
            date_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT,
            verified BOOLEAN DEFAULT 0,
            rhino_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data
    sample_incidents = [
        ('Rhino Poaching Incident - Kruger National Park', 'Two rhinos found dead with horns removed', 'Kruger National Park', 'Mpumalanga', '2024-01-15', 'DFFE Report', 1, 2),
        ('Suspected Poaching Activity - Hluhluwe-iMfolozi', 'Suspicious activity reported by rangers', 'Hluhluwe-iMfolozi Park', 'KwaZulu-Natal', '2024-01-20', 'SANParks Alert', 0, 1),
        ('Rhino Carcass Discovered - Pilanesberg', 'Adult rhino found deceased, investigation ongoing', 'Pilanesberg National Park', 'North West', '2024-01-25', 'Park Rangers', 1, 1),
        ('Poaching Attempt Thwarted - Marakele', 'Rangers intercepted poachers, no rhinos harmed', 'Marakele National Park', 'Limpopo', '2024-02-01', 'Anti-Poaching Unit', 1, 0),
        ('Rhino Monitoring Alert - Addo Elephant Park', 'Increased security after suspicious activity', 'Addo Elephant National Park', 'Eastern Cape', '2024-02-05', 'SANParks', 0, 0)
    ]
    
    for incident in sample_incidents:
        cursor.execute('''
            INSERT OR IGNORE INTO incidents 
            (title, description, location, province, date_occurred, source, verified, rhino_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', incident)
    
    # Insert default admin user (password: RhinoWatch2025!)
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash, role) 
        VALUES ('admin', 'admin@rhinowatchsa.org', 
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzrxgxu', 
                'admin')
    ''')
    
    conn.commit()
    conn.close()

def init_postgresql():
    """Initialize PostgreSQL database with sample data"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        database_url = os.environ.get('DATABASE_URL')
        url = urlparse(database_url)
        
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        
        # Create incidents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT,
                province TEXT,
                date_occurred DATE,
                date_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                verified BOOLEAN DEFAULT FALSE,
                rhino_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert sample data (only if tables are empty)
        cursor.execute('SELECT COUNT(*) FROM incidents')
        if cursor.fetchone()[0] == 0:
            sample_incidents = [
                ('Rhino Poaching Incident - Kruger National Park', 'Two rhinos found dead with horns removed', 'Kruger National Park', 'Mpumalanga', '2024-01-15', 'DFFE Report', True, 2),
                ('Suspected Poaching Activity - Hluhluwe-iMfolozi', 'Suspicious activity reported by rangers', 'Hluhluwe-iMfolozi Park', 'KwaZulu-Natal', '2024-01-20', 'SANParks Alert', False, 1),
                ('Rhino Carcass Discovered - Pilanesberg', 'Adult rhino found deceased, investigation ongoing', 'Pilanesberg National Park', 'North West', '2024-01-25', 'Park Rangers', True, 1),
                ('Poaching Attempt Thwarted - Marakele', 'Rangers intercepted poachers, no rhinos harmed', 'Marakele National Park', 'Limpopo', '2024-02-01', 'Anti-Poaching Unit', True, 0),
                ('Rhino Monitoring Alert - Addo Elephant Park', 'Increased security after suspicious activity', 'Addo Elephant National Park', 'Eastern Cape', '2024-02-05', 'SANParks', False, 0)
            ]
            
            for incident in sample_incidents:
                cursor.execute('''
                    INSERT INTO incidents 
                    (title, description, location, province, date_occurred, source, verified, rhino_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', incident)
        
        # Insert default admin user (only if users table is empty)
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role) 
                VALUES (%s, %s, %s, %s)
            ''', ('admin', 'admin@rhinowatchsa.org', 
                  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzrxgxu', 
                  'admin'))
        
        conn.commit()
        conn.close()
        
    except ImportError:
        print("PostgreSQL driver not available, falling back to SQLite")
        app.config['USE_POSTGRESQL'] = False
        init_sqlite()
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}, falling back to SQLite")
        app.config['USE_POSTGRESQL'] = False
        init_sqlite()

def get_db_connection():
    """Get database connection based on configuration"""
    if app.config.get('USE_POSTGRESQL'):
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            database_url = os.environ.get('DATABASE_URL')
            url = urlparse(database_url)
            
            return psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
        except:
            # Fallback to SQLite
            return sqlite3.connect(app.config['DATABASE_PATH'])
    else:
        return sqlite3.connect(app.config['DATABASE_PATH'])

# Initialize database on startup
init_db()

# Routes
@app.route('/')
def home():
    return jsonify({
        'message': 'Rhino Watch SA Dashboard API',
        'status': 'running',
        'platform': 'render.com',
        'version': '1.0.0',
        'database': 'postgresql' if app.config.get('USE_POSTGRESQL') else 'sqlite',
        'endpoints': {
            'health': '/health',
            'incidents': '/api/incidents',
            'stats': '/api/stats',
            'auth': '/api/auth/login',
            'dashboard': '/dashboard'
        }
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'rhino-watch-sa',
        'platform': 'render.com',
        'timestamp': datetime.now().isoformat(),
        'database': 'postgresql' if app.config.get('USE_POSTGRESQL') else 'sqlite'
    })

@app.route('/api/incidents')
def get_incidents():
    """Get all incidents with optional filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        province = request.args.get('province')
        verified = request.args.get('verified')
        limit = request.args.get('limit', 50, type=int)
        
        # Build query
        if app.config.get('USE_POSTGRESQL'):
            query = "SELECT * FROM incidents WHERE 1=1"
            params = []
            
            if province:
                query += " AND province = %s"
                params.append(province)
            
            if verified is not None:
                query += " AND verified = %s"
                params.append(verified.lower() == 'true')
            
            query += " ORDER BY date_occurred DESC LIMIT %s"
            params.append(limit)
        else:
            query = "SELECT * FROM incidents WHERE 1=1"
            params = []
            
            if province:
                query += " AND province = ?"
                params.append(province)
            
            if verified is not None:
                query += " AND verified = ?"
                params.append(1 if verified.lower() == 'true' else 0)
            
            query += " ORDER BY date_occurred DESC LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        incidents = []
        
        for row in cursor.fetchall():
            incidents.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'location': row[3],
                'province': row[4],
                'date_occurred': row[5],
                'date_reported': row[6],
                'source': row[7],
                'verified': bool(row[8]),
                'rhino_count': row[9],
                'created_at': row[10]
            })
        
        conn.close()
        return jsonify(incidents)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/incidents/<int:incident_id>')
def get_incident(incident_id):
    """Get specific incident by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if app.config.get('USE_POSTGRESQL'):
            cursor.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,))
        else:
            cursor.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        
        row = cursor.fetchone()
        
        if row:
            incident = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'location': row[3],
                'province': row[4],
                'date_occurred': row[5],
                'date_reported': row[6],
                'source': row[7],
                'verified': bool(row[8]),
                'rhino_count': row[9],
                'created_at': row[10]
            }
            conn.close()
            return jsonify(incident)
        
        conn.close()
        return jsonify({'error': 'Incident not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_statistics():
    """Get dashboard statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total incidents
        cursor.execute("SELECT COUNT(*) FROM incidents")
        total_incidents = cursor.fetchone()[0]
        
        # Verified incidents
        if app.config.get('USE_POSTGRESQL'):
            cursor.execute("SELECT COUNT(*) FROM incidents WHERE verified = true")
        else:
            cursor.execute("SELECT COUNT(*) FROM incidents WHERE verified = 1")
        verified_incidents = cursor.fetchone()[0]
        
        # Total rhinos affected
        cursor.execute("SELECT SUM(rhino_count) FROM incidents")
        total_rhinos = cursor.fetchone()[0] or 0
        
        # Incidents by province
        cursor.execute("SELECT province, COUNT(*) FROM incidents GROUP BY province")
        provinces = dict(cursor.fetchall())
        
        # Recent incidents (last 30 days)
        if app.config.get('USE_POSTGRESQL'):
            cursor.execute("""
                SELECT COUNT(*) FROM incidents 
                WHERE date_occurred >= CURRENT_DATE - INTERVAL '30 days'
            """)
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM incidents 
                WHERE date_occurred >= date('now', '-30 days')
            """)
        recent_incidents = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_incidents': total_incidents,
            'verified_incidents': verified_incidents,
            'total_rhinos_affected': total_rhinos,
            'recent_incidents': recent_incidents,
            'provinces': provinces,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if app.config.get('USE_POSTGRESQL'):
            cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = %s", (username,))
        else:
            cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username,))
        
        user = cursor.fetchone()
        
        if user and check_password_hash(user[2], password):
            access_token = create_access_token(
                identity=user[0],
                additional_claims={'username': user[1], 'role': user[3]}
            )
            
            conn.close()
            
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3]
                }
            })
        
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/protected')
@jwt_required()
def protected():
    """Protected route example"""
    current_user = get_jwt_identity()
    return jsonify({'user_id': current_user, 'message': 'Access granted'})

@app.route('/dashboard')
def dashboard():
    """Simple web dashboard"""
    dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rhino Watch SA Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }
        .platform-info {
            background: #3498db;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #2ecc71;
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
        }
        .incidents {
            margin-top: 30px;
        }
        .incident {
            border: 1px solid #ddd;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
            background: #f9f9f9;
        }
        .incident-title {
            font-weight: bold;
            color: #2c3e50;
        }
        .incident-meta {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .verified {
            background: #2ecc71;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }
        .unverified {
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }
        .loading {
            text-align: center;
            color: #7f8c8d;
        }
        .api-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦏 Rhino Watch SA Dashboard</h1>
            <p>Monitoring rhino poaching incidents in South Africa</p>
        </div>
        
        <div class="platform-info">
            <strong>🚀 Deployed on Render.com</strong> - Free Tier Hosting
        </div>
        
        <div class="stats" id="stats">
            <div class="loading">Loading statistics...</div>
        </div>
        
        <div class="incidents">
            <h2>Recent Incidents</h2>
            <div id="incidents">
                <div class="loading">Loading incidents...</div>
            </div>
        </div>
        
        <div class="api-info">
            <h3>API Endpoints</h3>
            <ul>
                <li><strong>GET /api/stats</strong> - Dashboard statistics</li>
                <li><strong>GET /api/incidents</strong> - List all incidents</li>
                <li><strong>GET /api/incidents/{id}</strong> - Get specific incident</li>
                <li><strong>POST /api/auth/login</strong> - User authentication</li>
                <li><strong>GET /health</strong> - Health check</li>
            </ul>
            <p><strong>Default Login:</strong> admin / RhinoWatch2025!</p>
        </div>
    </div>

    <script>
        // API base URL
        const API_BASE = window.location.origin;
        
        // Load statistics
        fetch(`${API_BASE}/api/stats`)
            .then(response => response.json())
            .then(data => {
                const statsContainer = document.getElementById('stats');
                statsContainer.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${data.total_incidents}</div>
                        <div>Total Incidents</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.verified_incidents}</div>
                        <div>Verified Incidents</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.total_rhinos_affected}</div>
                        <div>Rhinos Affected</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.recent_incidents}</div>
                        <div>Recent (30 days)</div>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error loading stats:', error);
                document.getElementById('stats').innerHTML = '<div class="loading">Error loading statistics</div>';
            });
        
        // Load incidents
        fetch(`${API_BASE}/api/incidents?limit=10`)
            .then(response => response.json())
            .then(data => {
                const incidentsContainer = document.getElementById('incidents');
                if (data.length === 0) {
                    incidentsContainer.innerHTML = '<div class="loading">No incidents found</div>';
                    return;
                }
                
                incidentsContainer.innerHTML = data.map(incident => `
                    <div class="incident">
                        <div class="incident-title">${incident.title}</div>
                        <div class="incident-meta">
                            📍 ${incident.location}, ${incident.province} | 
                            📅 ${incident.date_occurred} | 
                            📊 ${incident.rhino_count} rhino(s) affected |
                            <span class="${incident.verified ? 'verified' : 'unverified'}">
                                ${incident.verified ? 'Verified' : 'Unverified'}
                            </span>
                        </div>
                        ${incident.description ? `<div style="margin-top: 10px;">${incident.description}</div>` : ''}
                    </div>
                `).join('');
            })
            .catch(error => {
                console.error('Error loading incidents:', error);
                document.getElementById('incidents').innerHTML = '<div class="loading">Error loading incidents</div>';
            });
    </script>
</body>
</html>
    '''
    return render_template_string(dashboard_html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

