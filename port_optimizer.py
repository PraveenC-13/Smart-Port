from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
import random
import time

app = Flask(__name__)
# Allow cross-origin requests from frontend for local development
CORS(app)

# data Generation
def simulate_port_data(num_days=100):
    """Simulates daily port operation metrics."""
    data = []
    # Set a random seed for reproducibility in a single run
    random.seed(int(time.time() * 1000))
    for _ in range(num_days):
        # Cargo volume (50-150 tons)
        cargo_volume = random.randint(50, 150)
        # Ships arrived (5-20)
        ships_arrived = random.randint(5, 20)
        # Equipment status (0=OK, 1=Needs Maintenance)
        equipment_status = random.choice([0, 1])
        # Delay minutes (0-120 min)
        delay_minutes = random.randint(0, 120)
        data.append([cargo_volume, ships_arrived, equipment_status, delay_minutes])
    return np.array(data)

# Preprocessing
def preprocess_data(data):
    """Normalizes the input data features (0 to 1)."""
    min_vals = data.min(axis=0)
    max_vals = data.max(axis=0)
    # Use max_vals - min_vals + 1e-9 to prevent division by zero
    normalized = (data - min_vals) / (max_vals - min_vals + 1e-9)
    return normalized

# Meta Learner AI optimizer
class MetaLearner:
    """Simulates an AI that proposes and evaluates workflow parameters."""
    def __init__(self):
        self.best_workflow_param = None
        # Initialize with a high score (minimization problem)
        self.best_score = float('inf')

    def propose_workflow(self):
        """Proposes a new workflow parameter between 0 and 1."""
        return random.uniform(0, 1)

    def evaluate_workflow(self, workflow_param, simulation_results):
        """
        Evaluates the workflow based on the simulated results.
        The score minimizes average delay but heavily penalizes low parameters.
        Low parameter means less intervention, which is usually worse for delay.
        """
        # Feature 3 is the normalized delay (simulated_data[:, 3])
        avg_delay = np.mean(simulation_results[:, 3])
        # Minimize: (Avg Delay) + (Penalty for low workflow effort)
        # The score should decrease as the parameter moves towards the optimal setting.
        return avg_delay * (2 - workflow_param) # Score will be minimized when delay is low and param is high

    def update(self, workflow_param, score):
        """Updates the best parameter if the current score is better."""
        if score < self.best_score:
            self.best_score = score
            self.best_workflow_param = workflow_param

# Digital Twin Simulation
def run_simulation(workflow_param, port_data):
    """
    Simulates the port operation with an applied workflow optimization.
    The optimization reduces delay based on the workflow_param (0 to 1).
    """
    sim_data = port_data.copy()
    # Assume the workflow optimization reduces normalized delay (feature index 3)
    # A parameter of 1.0 means the maximum theoretical improvement (e.g., -50 units of normalized delay reduction)
    sim_data[:, 3] = np.maximum(0, sim_data[:, 3] - 0.5 * workflow_param)
    return sim_data

# Self-Evolving Workflow Training (FIXED: Converts bool to string)
def self_evolving_workflow(data, epochs=30):
    """Runs the optimization training loop and records every step."""
    learner = MetaLearner()
    history = []  # To store optimization steps for visualization

    for epoch in range(epochs):
        workflow_param = learner.propose_workflow()
        sim_results = run_simulation(workflow_param, data)
        score = learner.evaluate_workflow(workflow_param, sim_results)
        
        # Check if the new score is the best so far for visualization highlight
        is_new_best = score < learner.best_score
        
        learner.update(workflow_param, score)
        
        history.append({
            "epoch": epoch + 1,
            "param": round(workflow_param, 4),
            "score": round(score, 4),
            # FIX applied here: Convert boolean to string so Flask can serialize it to JSON
            "is_best": "true" if is_new_best else "false"
        })
        
    final_simulation = run_simulation(learner.best_workflow_param, data)
    simulation_sample = final_simulation[:5].tolist()

    return learner.best_workflow_param, learner.best_score, history, simulation_sample

# API Routes
@app.route('/run-simulation', methods=['GET'])
def run_simulation_api():
    raw_data = simulate_port_data(100)
    # The optimization is performed on normalized data
    processed_data = preprocess_data(raw_data)
    
    # Get optimization history
    best_param, best_score, history, simulation_sample = self_evolving_workflow(processed_data)

    return jsonify({
        "best_param": round(best_param, 4),
        "best_score": round(best_score, 4),
        "optimization_history": history,
        "simulation_sample": simulation_sample
    })

@app.route('/raw-port-data', methods=['GET'])
def get_raw_port_data():
    """Returns a sample of raw, unoptimized port data."""
    raw_data = simulate_port_data(100)
    data_list = [
        {
            "day": i + 1,
            "cargo_volume_tons": int(row[0]),
            "ships_arrived": int(row[1]),
            "equipment_status": "OK" if row[2] == 0 else "Needs Maintenance",
            "delay_minutes": int(row[3])
        }
        for i, row in enumerate(raw_data[:20]) # Limit to 20 days for display
    ]
    return jsonify(data_list)

if __name__ == "__main__":
    app.run(debug=True)
