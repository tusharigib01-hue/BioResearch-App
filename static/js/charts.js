// ===== Dashboard Charts =====

// ===== Sample Status Distribution (Doughnut) =====
const statusCtx = document.getElementById("statusChart").getContext("2d");
const statusChart = new Chart(statusCtx, {
  type: "doughnut",
  data: {
    labels: ["Active", "Used", "Archived"],
    datasets: [{
      data: [active_samples, used_samples, archived_samples], // pass values from Flask
      backgroundColor: [
        'rgba(79, 139, 201, 0.85)',
        'rgba(0, 200, 83, 0.85)',
        'rgba(142, 68, 173, 0.85)'
      ],
      borderColor: '#fff',
      borderWidth: 2
    }]
  },
  options: {
    responsive: true,
    cutout: '40%', // makes it a doughnut
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          font: { size: 14 },
          color: '#333'
        }
      },
      tooltip: {
        enabled: true
      }
    }
  }
});

// ===== Samples per Project (Bar) =====
const projectCtx = document.getElementById("projectChart").getContext("2d");
const projectChart = new Chart(projectCtx, {
  type: "bar",
  data: {
    labels: project_labels, // pass array of project names from Flask
    datasets: [{
      label: "Number of Samples",
      data: project_counts, // array of sample counts
      backgroundColor: 'rgba(79, 139, 201, 0.85)',
      borderRadius: 6,
      barPercentage: 0.6
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: true }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          color: '#333',
          font: { size: 14 }
        },
        grid: { color: 'rgba(0,0,0,0.05)' }
      },
      x: {
        ticks: {
          color: '#333',
          font: { size: 14 }
        },
        grid: { display: false }
      }
    }
  }
});
