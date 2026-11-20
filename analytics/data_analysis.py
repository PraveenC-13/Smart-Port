"""
Python Data Analysis Module for Smart Ports Operational Simulation.

Utilizes Pandas and NumPy to perform rigorous exploratory and operational
analytics on simulation outputs:
  1. Average vessel waiting time & distribution
  2. Daily vessel traffic & throughput patterns
  3. Berth utilization efficiency
  4. Vessel delays segmented by cargo priority
  5. Weather impact on waiting times & severe delays
  6. Operational efficiency trends (baseline vs. AI-optimized delay reduction)

Generates structured statistical summaries and exports them as CSV and JSON.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# Ensure parent directory is accessible
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from analytics.export_pipeline import export_all, EXPORTS_DIR


class PortAnalyticsEngine:
    def __init__(self, vessels_df=None):
        if vessels_df is None:
            csv_path = os.path.join(EXPORTS_DIR, 'vessel_simulation_results.csv')
            if os.path.exists(csv_path):
                self.df = pd.read_csv(csv_path)
            else:
                self.df, _, _ = export_all()
        else:
            self.df = vessels_df.copy()

    def overall_kpis(self):
        """Calculates core top-level port operational KPIs."""
        total_vessels = int(len(self.df))
        avg_wait = float(np.mean(self.df['Waiting_Time_Minutes']))
        median_wait = float(np.median(self.df['Waiting_Time_Minutes']))
        std_wait = float(np.std(self.df['Waiting_Time_Minutes']))
        min_wait = int(np.min(self.df['Waiting_Time_Minutes']))
        max_wait = int(np.max(self.df['Waiting_Time_Minutes']))

        avg_occupancy = float(np.mean(self.df['Berth_Occupancy_Pct']))
        total_original_delay = int(np.sum(self.df['Original_Delay_Minutes']))
        total_optimized_delay = int(np.sum(self.df['Optimized_Delay_Minutes']))
        total_delay_saved = total_original_delay - total_optimized_delay
        efficiency_gain_pct = round((total_delay_saved / total_original_delay) * 100, 2)

        high_priority_count = int((self.df['Cargo_Priority'] == 'High').sum())
        standard_priority_count = int((self.df['Cargo_Priority'] == 'Standard').sum())

        return {
            'total_vessels_handled': total_vessels,
            'avg_waiting_time_minutes': round(avg_wait, 2),
            'median_waiting_time_minutes': round(median_wait, 2),
            'std_waiting_time_minutes': round(std_wait, 2),
            'min_waiting_time_minutes': min_wait,
            'max_waiting_time_minutes': max_wait,
            'avg_berth_occupancy_pct': round(avg_occupancy, 2),
            'total_original_delay_min': total_original_delay,
            'total_optimized_delay_min': total_optimized_delay,
            'total_delay_saved_min': total_delay_saved,
            'port_efficiency_gain_pct': efficiency_gain_pct,
            'high_priority_vessels': high_priority_count,
            'standard_priority_vessels': standard_priority_count
        }

    def analyze_cargo_priority(self):
        """Analyzes operational delays and waiting times by cargo priority."""
        summary = self.df.groupby('Cargo_Priority').agg(
            Vessel_Count=('Vessel_ID', 'count'),
            Avg_Original_Delay=('Original_Delay_Minutes', 'mean'),
            Avg_Optimized_Delay=('Optimized_Delay_Minutes', 'mean'),
            Avg_Waiting_Time=('Waiting_Time_Minutes', 'mean'),
            Median_Waiting_Time=('Waiting_Time_Minutes', 'median'),
            Avg_Cranes=('Allocated_Cranes', 'mean'),
            Avg_Trucks=('Allocated_Trucks', 'mean'),
            Avg_Berth_Occupancy=('Berth_Occupancy_Pct', 'mean')
        ).reset_index()

        summary['Delay_Reduction_Pct'] = (
            (summary['Avg_Original_Delay'] - summary['Avg_Optimized_Delay']) / summary['Avg_Original_Delay'] * 100
        ).round(2)
        summary['Avg_Original_Delay'] = summary['Avg_Original_Delay'].round(2)
        summary['Avg_Optimized_Delay'] = summary['Avg_Optimized_Delay'].round(2)
        summary['Avg_Waiting_Time'] = summary['Avg_Waiting_Time'].round(2)
        summary['Avg_Cranes'] = summary['Avg_Cranes'].round(2)
        summary['Avg_Trucks'] = summary['Avg_Trucks'].round(2)
        summary['Avg_Berth_Occupancy'] = summary['Avg_Berth_Occupancy'].round(2)

        return summary

    def analyze_weather_impact(self):
        """Analyzes the impact of weather conditions on vessel delays and waiting queues."""
        weather_summary = self.df.groupby('Weather_Condition').agg(
            Vessel_Count=('Vessel_ID', 'count'),
            Avg_Waiting_Time_Min=('Waiting_Time_Minutes', 'mean'),
            Std_Waiting_Time=('Waiting_Time_Minutes', 'std'),
            Max_Waiting_Time=('Waiting_Time_Minutes', 'max'),
            Avg_Original_Delay=('Original_Delay_Minutes', 'mean'),
            Avg_Optimized_Delay=('Optimized_Delay_Minutes', 'mean'),
            Severe_Delays=('Delay_Category', lambda x: (x == 'Severe Delay').sum())
        ).reset_index()

        weather_summary['Avg_Waiting_Time_Min'] = weather_summary['Avg_Waiting_Time_Min'].round(2)
        weather_summary['Std_Waiting_Time'] = weather_summary['Std_Waiting_Time'].round(2)
        weather_summary['Avg_Original_Delay'] = weather_summary['Avg_Original_Delay'].round(2)
        weather_summary['Avg_Optimized_Delay'] = weather_summary['Avg_Optimized_Delay'].round(2)
        weather_summary['Severe_Delay_Rate_Pct'] = (
            weather_summary['Severe_Delays'] / weather_summary['Vessel_Count'] * 100
        ).round(2)

        return weather_summary.sort_values(by='Avg_Waiting_Time_Min', ascending=False)

    def analyze_berth_performance(self):
        """Analyzes utilization, crane resource distribution, and turnaround across berths."""
        berth_summary = self.df.groupby('Berth_ID').agg(
            Vessel_Count=('Vessel_ID', 'count'),
            Avg_Occupancy_Pct=('Berth_Occupancy_Pct', 'mean'),
            Min_Occupancy_Pct=('Berth_Occupancy_Pct', 'min'),
            Max_Occupancy_Pct=('Berth_Occupancy_Pct', 'max'),
            Avg_Waiting_Time=('Waiting_Time_Minutes', 'mean'),
            Total_Cranes_Deployed=('Allocated_Cranes', 'sum'),
            Avg_Cranes_Per_Vessel=('Allocated_Cranes', 'mean')
        ).reset_index()

        berth_summary['Avg_Occupancy_Pct'] = berth_summary['Avg_Occupancy_Pct'].round(2)
        berth_summary['Avg_Waiting_Time'] = berth_summary['Avg_Waiting_Time'].round(2)
        berth_summary['Avg_Cranes_Per_Vessel'] = berth_summary['Avg_Cranes_Per_Vessel'].round(2)

        return berth_summary

    def analyze_delay_distribution(self):
        """Breaks down vessel wait times into operational tiers."""
        distribution = self.df['Delay_Category'].value_counts().reset_index()
        distribution.columns = ['Delay_Category', 'Vessel_Count']
        distribution['Percentage'] = (distribution['Vessel_Count'] / len(self.df) * 100).round(2)
        return distribution

    def generate_full_report(self):
        """Generates all analytical summaries and saves them to analytics/exports/."""
        kpis = self.overall_kpis()
        priority_df = self.analyze_cargo_priority()
        weather_df = self.analyze_weather_impact()
        berth_df = self.analyze_berth_performance()
        delay_dist_df = self.analyze_delay_distribution()

        # Save CSV summaries
        priority_csv = os.path.join(EXPORTS_DIR, 'summary_cargo_priority.csv')
        priority_df.to_csv(priority_csv, index=False)

        weather_csv = os.path.join(EXPORTS_DIR, 'summary_weather_impact.csv')
        weather_df.to_csv(weather_csv, index=False)

        berth_csv = os.path.join(EXPORTS_DIR, 'summary_berth_performance.csv')
        berth_df.to_csv(berth_csv, index=False)

        dist_csv = os.path.join(EXPORTS_DIR, 'summary_delay_distribution.csv')
        delay_dist_df.to_csv(dist_csv, index=False)

        # Save KPI JSON
        kpis_json = os.path.join(EXPORTS_DIR, 'summary_kpis.json')
        with open(kpis_json, 'w') as f:
            json.dump(kpis, f, indent=4)

        return {
            'kpis': kpis,
            'cargo_priority': priority_df,
            'weather_impact': weather_df,
            'berth_performance': berth_df,
            'delay_distribution': delay_dist_df
        }


def print_cli_summary(report):
    print("=" * 70)
    print("SMART PORTS OPERATIONAL SIMULATION - STATISTICAL ANALYSIS REPORT")
    print("=" * 70)
    kpis = report['kpis']
    print(f"Total Vessels Analyzed:      {kpis['total_vessels_handled']}")
    print(f"Average Vessel Waiting Time: {kpis['avg_waiting_time_minutes']} minutes (Median: {kpis['median_waiting_time_minutes']}m, Std: {kpis['std_waiting_time_minutes']}m)")
    print(f"Average Berth Occupancy:     {kpis['avg_berth_occupancy_pct']}%")
    print(f"Baseline Delay:              {kpis['total_original_delay_min']} minutes")
    print(f"Optimized Delay:             {kpis['total_optimized_delay_min']} minutes")
    print(f"Net Port Delay Reduction:    {kpis['total_delay_saved_min']} minutes ({kpis['port_efficiency_gain_pct']}% improvement)")
    print(f"Priority Cargo Mix:          {kpis['high_priority_vessels']} High-Priority / {kpis['standard_priority_vessels']} Standard")
    print("-" * 70)
    print("\n[1] DELAY & WAITING TIME BY CARGO PRIORITY:")
    print(report['cargo_priority'].to_string(index=False))
    print("\n[2] WEATHER IMPACT ON WAITING TIMES & SEVERE DELAYS:")
    print(report['weather_impact'].to_string(index=False))
    print("\n[3] BERTH UTILIZATION & RESOURCE ALLOCATION:")
    print(report['berth_performance'].to_string(index=False))
    print("\n[4] DELAY CATEGORY DISTRIBUTION:")
    print(report['delay_distribution'].to_string(index=False))
    print("=" * 70)


if __name__ == '__main__':
    engine = PortAnalyticsEngine()
    report = engine.generate_full_report()
    print_cli_summary(report)
