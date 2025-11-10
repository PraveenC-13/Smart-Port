from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
import random

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# data Generation
def simulate_port_data(num_days=100):
    data = []
    for _ in range(num_days):
        cargo_volume = random.randint(50, 150)
        ships_arrived = random.randint(5, 20)
        equipment_status = random.choice([0, 1])
        delay_minutes = random.randint(0, 120)
        data.append([cargo_volume, ships_arrived, equipment_status, delay_minutes])
    return np.array(data)

# Preprocessing
def preprocess_data(data):
    min_vals = data.min(axis=0)
    max_vals = data.max(axis=0)
    normalized = (data - min_vals) / (max_vals - min_vals + 1e-9)
    return normalized

#Meta Learner AI optimizer
class MetaLearner:
    def __init__(self):
        self.best_workflow_param = None
        self.best_score = float('inf')

    def propose_workflow(self):
        return random.uniform(0, 1)

    def evaluate_workflow(self, workflow_param, simulation_results):
        avg_delay = np.mean(simulation_results[:, 3])
        return avg_delay * (1 - workflow_param)

    def update(self, workflow_param, score):
        if score < self.best_score:
            self.best_score = score
            self.best_workflow_param = workflow_param

#Digital Twin Simulation
def run_simulation(workflow_param, port_data):
    sim_data = port_data.copy()
    sim_data[:, 3] = np.maximum(0, sim_data[:, 3] - 50 * workflow_param)
    return sim_data

#Self-Evolving Workflow Training
def self_evolving_workflow(data, epochs=30):
    learner = MetaLearner()
    for _ in range(epochs):
        workflow_param = learner.propose_workflow()
        sim_results = run_simulation(workflow_param, data)
        score = learner.evaluate_workflow(workflow_param, sim_results)
        learner.update(workflow_param, score)
    return learner.best_workflow_param, learner.best_score

#API Routes
@app.route('/run-simulation', methods=['GET'])
def run_simulation_api():
    raw_data = simulate_port_data(100)
    processed_data = preprocess_data(raw_data)
    best_param, best_score = self_evolving_workflow(processed_data)
    final_simulation = run_simulation(best_param, processed_data)
    simulation_sample = final_simulation[:5].tolist()

    return jsonify({
        "best_param": round(best_param, 3),
        "best_score": round(best_score, 3),
        "simulation_sample": simulation_sample
    })

@app.route('/raw-port-data', methods=['GET'])
def get_raw_port_data():
    raw_data = simulate_port_data(100)
    data_list = [
        {
            "day": i + 1,
            "cargo_volume_tons": int(row[0]),
            "ships_arrived": int(row[1]),
            "equipment_status": "OK" if row[2] == 0 else "Needs Maintenance",
            "delay_minutes": int(row[3])
        }
        for i, row in enumerate(raw_data)
    ]
    return jsonify(data_list)

if __name__ == "__main__":
    app.run(debug=True)
