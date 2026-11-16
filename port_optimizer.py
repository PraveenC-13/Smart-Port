from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import random
import time
import os

# --- 1. APP & DATABASE SETUP ---
app = Flask(__name__, template_folder='template') 
CORS(app)

# Configure Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'port_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db = SQLAlchemy(app)

# --- 2. DATABASE MODELS ---
class SimulationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    best_score = db.Column(db.Float)
    best_param = db.Column(db.Float)
    improvement_rate = db.Column(db.Float)

# Create the database and tables
with app.app_context():
    db.create_all()

# --- 3. CONFIGURATION AND DATA SIMULATION ---
MAX_DELAY = 120 
NUM_EPOCHS = 30 
SIMULATION_DAYS = 100 

PRIORITY_CARGO = ['Food (Perishable)', 'Meat (Frozen/Chilled)', 'Medical Supplies', 'Live Animals', 'Hazardous Materials']
NORMAL_CARGO = ['Electronics', 'Textiles', 'Automobile Parts', 'Raw Materials']
WEATHER_CONDITIONS = ['Clear', 'Light Rain', 'Heavy Rain', 'Windy', 'Fog']

def generate_baseline_data():
    data = []
    for day in range(1, SIMULATION_DAYS + 1):
        cargo_type = random.choice(PRIORITY_CARGO + NORMAL_CARGO)
        weather = random.choice(WEATHER_CONDITIONS)
        base_delay = random.randint(30, 90)
        if weather in ['Heavy Rain', 'Windy']:
            base_delay += random.randint(20, 30)
        if cargo_type in PRIORITY_CARGO:
            base_delay += random.randint(10, 30)
        base_delay = min(base_delay, MAX_DELAY)

        data.append({
            'day': day,
            'ship_id': f"SHIP-{day:03d}",
            'cargo_type': cargo_type,
            'delay_minutes': base_delay,
            'weather_condition': weather, 
            'berth_status': random.choice(['Assigned', 'Pending']),
            'maintenance_cranes': random.randint(0, 2), 
        })
    return data

RAW_PORT_DATA = generate_baseline_data()

def run_digital_twin(workflow_param, raw_data):
    total_score = 0
    optimized_sample = [] 
    for ship in raw_data:
        optimization_factor = workflow_param * 0.5 
        if ship['cargo_type'] in PRIORITY_CARGO:
            priority_weight = 3.0
            allocated_cranes = random.randint(3, 5) if workflow_param > 0.6 else random.randint(2, 3)
            allocated_trucks = random.randint(10, 15) if workflow_param > 0.6 else random.randint(5, 10)
            allocated_berth = "B-A1 (Priority)"
            crane_status = "Operational"
            notes = "Expedited clearance due to priority cargo."
            effective_delay = max(20, ship['delay_minutes'] * (1 - optimization_factor * 1.5)) 
        else:
            priority_weight = 1.0
            allocated_cranes = random.randint(1, 2)
            allocated_trucks = random.randint(3, 7)
            allocated_berth = random.choice(["B-B2", "B-C3", "B-D4"])
            crane_status = random.choice(["Operational", "Under Light Maintenance"])
            notes = "Standard workflow applied."
            effective_delay = max(20, ship['delay_minutes'] * (1 - optimization_factor * 0.7))

        weather_penalty = 1.2 if ship['weather_condition'] in ['Heavy Rain', 'Windy'] and workflow_param < 0.5 else 1.0
        weighted_delay = effective_delay * priority_weight
        score = weighted_delay * (2.0 - workflow_param) * weather_penalty
        total_score += score
        
        optimized_sample.append({
            'ship_id': ship['ship_id'],
            'priority_assigned': "High" if ship['cargo_type'] in PRIORITY_CARGO else "Standard",
            'optimized_delay_min': int(effective_delay),
            'allocated_cranes': allocated_cranes,
            'allocated_trucks': allocated_trucks,
            'allocated_berth': allocated_berth,
            'crane_maintenance_status': crane_status,
            'digital_twin_notes': notes,
        })
    return total_score / len(raw_data), optimized_sample 

# --- 4. FLASK ENDPOINTS ---

@app.route('/')
def index():
    return render_template('port_dashboard.html')

@app.route('/raw-port-data', methods=['GET'])
def get_raw_data_sample():
    sample_data = []
    for i, ship in enumerate(RAW_PORT_DATA[:5]):
        sample_data.append({
            'day': i + 1,
            'ship_id': ship['ship_id'],
            'cargo_type': ship['cargo_type'],
            'weather_condition': ship['weather_condition'],
            'original_delay': ship['delay_minutes']
        })
    return jsonify(sample_data)

@app.route('/run-simulation', methods=['GET'])
def run_simulation():
    best_score = float('inf')
    best_param = 0
    best_sample_data_list = []
    
    for epoch in range(1, NUM_EPOCHS + 1):
        workflow_param = round(random.uniform(0.1, 0.95), 4) 
        avg_score, sample_data = run_digital_twin(workflow_param, RAW_PORT_DATA)
        if avg_score < best_score:
            best_score = avg_score
            best_param = workflow_param
            best_sample_data_list = sample_data
        time.sleep(0.01) 

    # Save to Database
    new_record = SimulationResult(best_score=best_score, best_param=best_param)
    db.session.add(new_record)
    db.session.commit()
    print("Successfully saved simulation to database!")

    high_priority_sample = [s for s in best_sample_data_list if s['priority_assigned'] == 'High']
    dashboard_sample = random.choice(high_priority_sample) if high_priority_sample else best_sample_data_list[0]

    return jsonify({
        'status': 'complete',
        'best_score': round(best_score, 2),
        'best_param': f"{best_param:.4f}",
        'best_operation_description': "Optimal strategy for maximizing resource allocation.",
        'simulation_sample': [dashboard_sample] 
    })

# New Route: Get History of simulations
@app.route('/history', methods=['GET'])
def get_history():
    results = SimulationResult.query.order_by(SimulationResult.timestamp.desc()).limit(10).all()
    history_list = []
    for r in results:
        history_list.append({
            'id': r.id,
            'score': round(r.best_score, 2),
            'param': r.best_param,
            'time': r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(history_list)

if __name__ == '__main__':
    app.run(debug=True, port=5000)