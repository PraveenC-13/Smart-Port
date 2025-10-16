document.getElementById("startSim").addEventListener("click", () => {
  fetch("http://localhost:5000/run-simulation")
    .then(response => response.json())
    .then(data => {
      const output = document.getElementById("output");
      output.innerHTML = `
        <h3>Best Workflow Result</h3>
        <p><strong>Best Parameter:</strong> ${data.best_param}</p>
        <p><strong>Best Score:</strong> ${data.best_score}</p>
        <p><strong>Simulation Sample (first 5 rows):</strong></p>
        <pre>${JSON.stringify(data.simulation_sample, null, 2)}</pre>
      `;
    })
    .catch(error => {
      console.error("Error fetching simulation:", error);
      document.getElementById("output").textContent = "Failed to run simulation.";
    });
});

document.getElementById("showRaw").addEventListener("click", () => {
  fetch("http://localhost:5000/raw-port-data")
    .then(response => response.json())
    .then(data => {
      const output = document.getElementById("output");
      let html = "<h3>Raw Port Operation Data (100 Days)</h3><table border='1' cellpadding='5'><tr><th>Day</th><th>Cargo Volume (tons)</th><th>Ships Arrived</th><th>Equipment Status</th><th>Delay (minutes)</th></tr>";
      data.forEach(row => {
        html += `<tr>
            <td>${row.day}</td>
            <td>${row.cargo_volume_tons}</td>
            <td>${row.ships_arrived}</td>
            <td>${row.equipment_status}</td>
            <td>${row.delay_minutes}</td>
        </tr>`;
      });
      html += "</table>";
      output.innerHTML = html;
    })
    .catch(error => {
      console.error("Error fetching raw port data:", error);
      document.getElementById("output").textContent = "Failed to load port data.";
    });
});
