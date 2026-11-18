"""
Data Export Pipeline for Smart Ports Operational Simulation.

Extracts real simulation results from the 100-day baseline data and
SQLite simulation database, cleans/transforms the dataset using Pandas,
computes deterministic temporal and operational fields, and exports
cleaned CSV datasets ready for Excel and Microsoft Power BI.
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Ensure parent directory is in sys.path so we can import port_optimizer cleanly
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import existing simulation domain logic without breaking or modifying port_optimizer
from port_optimizer import (
    RAW_PORT_DATA,
    PRIORITY_CARGO,
    NORMAL_CARGO,
    WEATHER_CONDITIONS,
    run_digital_twin,
    basedir,
    SimulationResult
)

EXPORTS_DIR = os.path.join(basedir, 'analytics', 'exports')
os.makedirs(EXPORTS_DIR, exist_ok=True)


def get_latest_simulation_param():
    """
    Retrieves the best workflow parameter stored in the SQLite database.
    If none exists, falls back to running a simulated optimization step.
    """
    db_path = os.path.join(basedir, 'port_data.db')
    best_param = 0.85
    best_score = None

    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT best_param, best_score FROM simulation_result ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if row and row[0] is not None:
                best_param = float(row[0])
                best_score = float(row[1]) if row[1] is not None else None
        except Exception as e:
            print(f"[Warning] Could not read latest simulation from DB: {e}. Using default param.")

    return best_param, best_score


def generate_vessel_operations_dataset(workflow_param=None):
    """
    Extracts the 100-day port simulation data, blends it with the digital twin's
    operational resource allocations, and produces a complete, realistic dataset.

    Calculated Fields:
      - Arrival Time: Deterministic schedule based on simulation day + time-of-day offset.
      - Waiting Time: Waiting queue duration (delay_minutes before berthing).
      - Service Time: Hours required at berth (derived from cargo volume and crane allocation).
      - Departure Time: Arrival Time + Waiting Time + Service Time.
      - Delay Minutes: Baseline delay minus optimization savings.
      - Delay Category: 'On-Time/Low Delay' (<30m), 'Moderate Delay' (30-60m), 'Severe Delay' (>60m).
      - Berth Occupancy Rate (%): Hourly berth utilization efficiency based on allocated berth and turnaround.
    """
    if workflow_param is None:
        workflow_param, _ = get_latest_simulation_param()

    # Run digital twin on baseline data
    score, optimized_records = run_digital_twin(workflow_param, RAW_PORT_DATA)
    opt_by_id = {rec['ship_id']: rec for rec in optimized_records}

    base_simulation_start = datetime(2026, 1, 1, 8, 0, 0)
    records = []

    for ship in RAW_PORT_DATA:
        ship_id = ship['ship_id']
        day = ship['day']
        cargo = ship['cargo_type']
        weather = ship['weather_condition']
        raw_delay = ship['delay_minutes']
        berth_status = ship.get('berth_status', 'Assigned')
        maintenance_cranes = ship.get('maintenance_cranes', 0)

        opt = opt_by_id.get(ship_id, {})
        priority = opt.get('priority_assigned', 'High' if cargo in PRIORITY_CARGO else 'Standard')
        opt_delay = opt.get('optimized_delay_min', raw_delay)
        cranes = opt.get('allocated_cranes', 2)
        trucks = opt.get('allocated_trucks', 6)
        berth_id = opt.get('allocated_berth', 'B-B2')
        crane_status = opt.get('crane_maintenance_status', 'Operational')
        notes = opt.get('digital_twin_notes', 'Standard workflow applied.')

        # Deterministic arrival time on day N
        # Stagger vessel arrival across day: day 1 starts Jan 1, hour = (day * 7) % 18 + 5
        arrival_hour = 6 + (day * 3) % 12
        arrival_minute = (day * 17) % 60
        arrival_dt = base_simulation_start + timedelta(days=day - 1, hours=arrival_hour, minutes=arrival_minute)

        # Waiting time (delay prior to berth docking)
        waiting_time_minutes = opt_delay

        # Estimated service / handling duration at berth based on cranes and priority
        # More cranes reduce handling time; perishable priority gets swift turnaround
        base_handling_hours = 8.0 if priority == 'High' else 14.0
        handling_duration_hours = max(4.0, base_handling_hours - (cranes * 1.2))
        handling_minutes = int(handling_duration_hours * 60)

        # Departure time calculation
        departure_dt = arrival_dt + timedelta(minutes=waiting_time_minutes + handling_minutes)

        # Berth occupancy / utilization percentage for this vessel turnaround window
        # Berth operational capacity standard window is 24 hours per day
        berth_occupancy_pct = round(min(100.0, (handling_duration_hours / 24.0) * 100 + (waiting_time_minutes / 60.0) * 5), 2)

        # Delay categorization
        if waiting_time_minutes < 30:
            delay_category = 'Low / On-Time'
        elif waiting_time_minutes <= 60:
            delay_category = 'Moderate Delay'
        else:
            delay_category = 'Severe Delay'

        records.append({
            'Simulation_Day': day,
            'Vessel_ID': ship_id,
            'Cargo_Type': cargo,
            'Cargo_Priority': priority,
            'Weather_Condition': weather,
            'Arrival_Time': arrival_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'Departure_Time': departure_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'Original_Delay_Minutes': raw_delay,
            'Optimized_Delay_Minutes': opt_delay,
            'Waiting_Time_Minutes': waiting_time_minutes,
            'Berth_ID': berth_id,
            'Berth_Status': berth_status,
            'Berth_Occupancy_Pct': berth_occupancy_pct,
            'Allocated_Cranes': cranes,
            'Allocated_Trucks': trucks,
            'Crane_Maintenance_Cranes': maintenance_cranes,
            'Crane_Status': crane_status,
            'Delay_Category': delay_category,
            'Digital_Twin_Notes': notes
        })

    df = pd.DataFrame(records)

    # Data Quality & Cleaning:
    # 1. Ensure correct data types
    df['Simulation_Day'] = df['Simulation_Day'].astype(int)
    df['Waiting_Time_Minutes'] = df['Waiting_Time_Minutes'].astype(int)
    df['Optimized_Delay_Minutes'] = df['Optimized_Delay_Minutes'].astype(int)
    df['Berth_Occupancy_Pct'] = df['Berth_Occupancy_Pct'].astype(float)
    
    # 2. Assert no missing values and drop duplicates if any
    df = df.drop_duplicates(subset=['Vessel_ID'])
    df = df.fillna({
        'Original_Delay_Minutes': df['Original_Delay_Minutes'].median(),
        'Waiting_Time_Minutes': df['Waiting_Time_Minutes'].median()
    })

    return df


def generate_daily_port_metrics(vessels_df):
    """
    Rolls up vessel data into daily port performance metrics.
    Useful as a dimension/fact aggregation for Power BI and Excel models.
    """
    daily = vessels_df.groupby('Simulation_Day').agg(
        Total_Vessels=('Vessel_ID', 'count'),
        High_Priority_Vessels=('Cargo_Priority', lambda x: (x == 'High').sum()),
        Standard_Priority_Vessels=('Cargo_Priority', lambda x: (x == 'Standard').sum()),
        Avg_Waiting_Time_Min=('Waiting_Time_Minutes', 'mean'),
        Max_Waiting_Time_Min=('Waiting_Time_Minutes', 'max'),
        Avg_Berth_Occupancy_Pct=('Berth_Occupancy_Pct', 'mean'),
        Total_Cranes_Deployed=('Allocated_Cranes', 'sum'),
        Total_Trucks_Deployed=('Allocated_Trucks', 'sum'),
        Primary_Weather=('Weather_Condition', lambda x: x.mode()[0] if not x.empty else 'Clear')
    ).reset_index()

    # Round floats for clean reporting
    daily['Avg_Waiting_Time_Min'] = daily['Avg_Waiting_Time_Min'].round(2)
    daily['Avg_Berth_Occupancy_Pct'] = daily['Avg_Berth_Occupancy_Pct'].round(2)

    return daily


def generate_berth_utilization_metrics(vessels_df):
    """
    Aggregates berth-level operational analytics across the 100 simulation days.
    """
    berth_summary = vessels_df.groupby('Berth_ID').agg(
        Total_Vessels_Serviced=('Vessel_ID', 'count'),
        Avg_Berth_Occupancy_Pct=('Berth_Occupancy_Pct', 'mean'),
        Avg_Turnaround_Waiting_Min=('Waiting_Time_Minutes', 'mean'),
        Total_Cranes_Allocated=('Allocated_Cranes', 'sum'),
        Total_Trucks_Allocated=('Allocated_Trucks', 'sum')
    ).reset_index()

    berth_summary['Avg_Berth_Occupancy_Pct'] = berth_summary['Avg_Berth_Occupancy_Pct'].round(2)
    berth_summary['Avg_Turnaround_Waiting_Min'] = berth_summary['Avg_Turnaround_Waiting_Min'].round(2)

    return berth_summary


def export_all():
    """
    Runs the full export pipeline and generates CSVs in analytics/exports/
    """
    param, score = get_latest_simulation_param()
    print(f"[Export Pipeline] Utilizing best parameter: {param:.4f} (Score: {score})")

    # 1. Main vessel simulation log
    vessels_df = generate_vessel_operations_dataset(param)
    vessels_csv = os.path.join(EXPORTS_DIR, 'vessel_simulation_results.csv')
    vessels_df.to_csv(vessels_csv, index=False)
    print(f"[Saved] Vessel simulation dataset -> {vessels_csv} ({len(vessels_df)} rows)")

    # 2. Daily aggregated metrics
    daily_df = generate_daily_port_metrics(vessels_df)
    daily_csv = os.path.join(EXPORTS_DIR, 'daily_port_metrics.csv')
    daily_df.to_csv(daily_csv, index=False)
    print(f"[Saved] Daily port metrics -> {daily_csv} ({len(daily_df)} rows)")

    # 3. Berth utilization summary
    berth_df = generate_berth_utilization_metrics(vessels_df)
    berth_csv = os.path.join(EXPORTS_DIR, 'berth_utilization_summary.csv')
    berth_df.to_csv(berth_csv, index=False)
    print(f"[Saved] Berth utilization summary -> {berth_csv} ({len(berth_df)} rows)")

    return vessels_df, daily_df, berth_df


if __name__ == '__main__':
    v_df, d_df, b_df = export_all()
    print("\nSample Exported Vessel Data:")
    print(v_df[['Simulation_Day', 'Vessel_ID', 'Cargo_Priority', 'Weather_Condition', 'Waiting_Time_Minutes', 'Berth_ID', 'Berth_Occupancy_Pct']].head())
