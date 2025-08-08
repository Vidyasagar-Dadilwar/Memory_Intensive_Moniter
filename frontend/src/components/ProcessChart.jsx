import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const ProcessChart = ({ history }) => {
  const [chartData, setChartData] = useState({
    datasets: []
  });

  useEffect(() => {
    if (!history || history.length === 0) return;

    // Sort history by timestamp (oldest first)
    const sortedHistory = [...history].sort((a, b) => a.timestamp - b.timestamp);

    // Prepare data for chart
    const memoryData = sortedHistory.map(item => ({
      x: new Date(item.timestamp * 1000), // Convert to milliseconds
      y: item.memory_percent
    }));

    const cpuData = sortedHistory.map(item => ({
      x: new Date(item.timestamp * 1000),
      y: item.cpu_percent
    }));

    setChartData({
      datasets: [
        {
          label: 'Memory %',
          data: memoryData,
          borderColor: 'rgba(53, 162, 235, 1)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
          tension: 0.2,
          yAxisID: 'y'
        },
        {
          label: 'CPU %',
          data: cpuData,
          borderColor: 'rgba(255, 99, 132, 1)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          tension: 0.2,
          yAxisID: 'y1'
        }
      ]
    });
  }, [history]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: false
      },
      tooltip: {
        callbacks: {
          title: (context) => {
            const date = new Date(context[0].parsed.x);
            return date.toLocaleTimeString();
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'minute',
          displayFormats: {
            minute: 'HH:mm:ss'
          }
        },
        title: {
          display: true,
          text: 'Time'
        }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Memory %'
        },
        min: 0,
        suggestedMax: 100
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'CPU %'
        },
        min: 0,
        suggestedMax: 100,
        grid: {
          drawOnChartArea: false
        }
      }
    }
  };

  if (!history || history.length === 0) {
    return (
      <div className="chart-container d-flex justify-content-center align-items-center">
        <p className="text-muted">No historical data available</p>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <Line options={options} data={chartData} />
    </div>
  );
};

export default ProcessChart;