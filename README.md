<<<<<<< Updated upstream
## Features
- Reinforcement learning-based optimization
- Digital twin simulation
- Workflow analysis
- Resource allocation optimization
- Automated testing environment

## Tech Stack
- Python
- JavaScript
- HTML/CSS
- AI/ML Concepts

## Future Improvements

- Integrate live IoT sensor streams
- Cloud deployment using Docker and Kubernetes
- Predictive maintenance module
- Real-time analytics dashboard
- Multi-port support
=======
# Smart Ports Operational Simulation & Data Analytics Platform

An enterprise-grade operational simulation, optimization, and analytics project for maritime container port logistics. Built using **Python, Flask, NumPy, SQLite, Pandas, Microsoft Excel, and Power BI**.

---

## 1. System Architecture & End-to-End Data Flow

The project connects software engineering and data analytics into a cohesive operational intelligence pipeline:

```
+-----------------------------------------------------------------------------------------+
|                                1. OPERATIONAL SIMULATION                                |
|   - 100-Day baseline vessel traffic generator (Vessels, Cargo Types, Weather, Delays)   |
|   - Digital Twin Optimization Engine (AI Workflow Tuning, Cranes, Trucks, Berth)        |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                                  2. DATABASE PERSISTENCE                                |
|   - SQLite Database (`port_data.db`): `simulation_result` table                         |
|   - Stores epoch timestamps, best optimization parameters, and performance scores       |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                                   3. WEB APP & REST APIs                                |
|   - Flask backend (`port_optimizer.py` / `port_work.py`)                                |
|   - REST APIs: `/run-simulation`, `/raw-port-data`, `/history`                          |
|   - Interactive Web Dashboard (Tailwind CSS, Gauge charts, Live allocations)            |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                                4. DATA EXPORT PIPELINE                                  |
|   - `analytics/export_pipeline.py` extracts baseline + database records                 |
|   - Computes deterministic arrival/departure timestamps, service turnaround & occupancy |
|   - Validates data types, handles nulls, and deduplicates records                       |
|   - Exports CSVs: `vessel_simulation_results.csv`, `daily_port_metrics.csv`,            |
|     `berth_utilization_summary.csv`                                                     |
+-----------------------------------------------------------------------------------------+
                                             |
                     +-----------------------+-----------------------+
                     v                                               v
+-----------------------------------------+     +-----------------------------------------+
|           5. EXCEL ANALYTICS            |     |           6. POWER BI DASHBOARD         |
|   - `Smart_Ports_Analytics.xlsx`        |     |   - Multi-table star/snowflake model    |
|   - Raw Data & Cleaned Data Sheets      |     |   - Custom DAX measures library         |
|   - Dynamic formulas (SUM, AVERAGE,     |     |   - Executive visuals, slicers & cards  |
|     COUNTIF, AVERAGEIF, IF)             |     |   - Guided setup in `POWER_BI_GUIDE.md` |
|   - 4 Embedded OpenPyXL native charts   |     +-----------------------------------------+
+-----------------------------------------+
```

---

## 2. Project Directory Structure

```
PORT PRO/
├── port_optimizer.py               # Main Flask application & Digital Twin engine
├── port_work.py                    # Standalone simulation & meta-learning module
├── port_data.db                    # SQLite database storing simulation runs
├── template/                       # Web dashboard HTML templates
│   ├── portdash.html
│   ├── portoverview.html
│   ├── portlogin.html
│   └── index.html
├── static/                         # Frontend styling, scripts, and media assets
│   ├── css/
│   ├── js/
│   └── img/
├── analytics/                      # Data Analytics Extension
│   ├── export_pipeline.py          # Extracts simulation data and generates clean CSVs
│   ├── data_analysis.py            # Pandas & NumPy analysis module
│   ├── generate_excel.py           # Automated Excel workbook generator with formulas & charts
│   ├── Smart_Ports_Analytics.xlsx  # Professional 3-sheet Excel analytics workbook
│   ├── POWER_BI_GUIDE.md           # Step-by-step Power BI import, DAX, and visual design guide
│   └── exports/                    # Clean CSV datasets
│       ├── vessel_simulation_results.csv
│       ├── daily_port_metrics.csv
│       ├── berth_utilization_summary.csv
│       ├── summary_cargo_priority.csv
│       ├── summary_weather_impact.csv
│       ├── summary_berth_performance.csv
│       ├── summary_delay_distribution.csv
│       └── summary_kpis.json
└── README.md                       # Comprehensive project documentation
```

---

## 3. How to Run the Project

### Prerequisites
Make sure Python 3.10+ is installed along with required packages:
```bash
pip install flask flask-cors flask-sqlalchemy numpy pandas openpyxl
```

### Step 1: Run the Flask Web Application
```bash
python port_optimizer.py
```
Open your browser and navigate to:
- `http://127.0.0.1:5000/` - Interactive Port Operations Dashboard
- `http://127.0.0.1:5000/run-simulation` - Run Digital Twin optimization
- `http://127.0.0.1:5000/history` - View historical simulation runs

### Step 2: Run the Data Export Pipeline
```bash
python analytics/export_pipeline.py
```
This extracts the simulation outputs, queries `port_data.db` for the latest optimization parameters, and writes cleaned CSV datasets into `analytics/exports/`.

### Step 3: Run the Python Data Analysis Module
```bash
python analytics/data_analysis.py
```
This performs statistical analysis across vessel priorities, weather conditions, berth utilization, and generates formatted CSV/JSON summaries in `analytics/exports/`.

### Step 4: Generate the Excel Analytics Workbook
```bash
python analytics/generate_excel.py
```
This builds `analytics/Smart_Ports_Analytics.xlsx` containing:
- **Raw Data**: 100 days of input simulation records.
- **Cleaned Data**: 100 vessel rows with calculated arrival, departure, berth, delay categories, and occupancy rates.
- **Summary Analysis**: Dynamic Excel formulas (`AVERAGE`, `COUNTIF`, `AVERAGEIF`, `SUMIF`, `IF`) and 4 native charts.

### Step 5: Power BI Implementation
Refer to [POWER_BI_GUIDE.md](file:///D:/PORT%20PRO/analytics/POWER_BI_GUIDE.md) for full instructions on importing the CSV datasets into Power BI Desktop, configuring the relationships, and adding the DAX measures.

---

## 4. Key Performance Indicators (KPIs) Explained

| Metric | Definition | Practical Port Meaning |
| :--- | :--- | :--- |
| **Total Vessels Handled** | Total count of unique vessel calls over the 100-day window (`COUNTROWS`). | Measures port volume throughput and cargo capacity. |
| **Average Waiting Time (min)** | Mean duration vessels wait before docking and receiving berth access. | Core indicator of port congestion; lower is better. |
| **Average Berth Occupancy (%)** | Percentage of operational time a berth is actively handling container operations. | Measures quay asset utilization; balances productivity against berth starvation or overcrowding. |
| **Total Delay Saved (min)** | Cumulative reduction in vessel wait times achieved by dynamic resource allocation. | Demonstrates the tangible business return of the digital twin strategy. |
| **Efficiency Gain (%)** | `(Baseline Delay - Optimized Delay) / Baseline Delay * 100`. | Overall operational performance improvement percentage. |
| **Severe Delay Rate (%)** | Proportion of vessels delayed >60 minutes due to adverse weather or bottlenecks. | Risk and reliability metric evaluated under windy/storm conditions. |

---

## 5. Technical Interview Defense Guide

### Q1: "How does your data export pipeline ensure data integrity without inventing fake values?"
> **Answer:**  
> *"The export pipeline directly ingests the 100-day simulation records generated by the domain model and pairs them with the optimal parameter stored in SQLite (`port_data.db`). Rather than inventing synthetic metrics, we calculate realistic temporal and physical values using deterministic domain logic: arrival times are derived from the simulation day cycle, handling durations are calculated from crane allocations, departure times are the exact sum of arrival + waiting + service time, and berth occupancy rates reflect the proportion of the 24-hour quay window utilized. Pandas validates schema types, checks for nulls, and deduplicates vessel records before exporting."*

### Q2: "What is the analytical finding regarding cargo priority and weather impact?"
> **Answer:**  
> *"Our Pandas analysis and Excel pivot models revealed that High-Priority vessels (perishables, medical supplies, hazardous materials) experienced a **68.95% reduction in delay** because the Digital Twin assigned them dedicated berth B-A1 and allocated an average of ~4 cranes versus 1.6 cranes for standard cargo. Weather analysis showed that Windy conditions and Heavy Rain contributed to an average wait of 40–46 minutes with severe delays of ~20%, whereas Clear and Foggy days averaged under 30 minutes with zero severe delays."*

### Q3: "Why did you use both Excel formulas and Power BI DAX instead of only Python?"
> **Answer:**  
> *"In enterprise operations, different stakeholders require different toolsets. Python provides automated data pipeline engineering and statistical analysis. Excel enables operations managers to audit granular formulas (`COUNTIF`, `AVERAGEIF`, `IF`) and inspect static workbooks. Power BI provides executive leadership with interactive self-service dashboards, dynamic slicers, and relational DAX measures that recalculate instantaneously across multiple dimensions."*
>>>>>>> Stashed changes
