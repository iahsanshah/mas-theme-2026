$(document).ready(function() {
    function fetchEmployeeCountByDepartment() {
        $.ajax({
            url: "/api/method/hr_visulizations.api.get_dashboard_data",
            success: function(response) {
                if (response.message && response.message.employee_count_by_department) {
                    let data = response.message.employee_count_by_department;
                    let labels = data.map(item => item.department);
                    let values = data.map(item => item.employee_count);

                    createBarChart(
                        "employee_count_by_department",
                        'bar',
                        "Employee Count By Department",
                        { labels: labels, values: values },
                        ['#1976D2', '#64B5F6', '#90CAF9', '#E3F2FD'],
                        "y"
                    );
                } else {
                    console.error("Invalid response format:", response);
                }
            },
            error: function(xhr, status, error) {
                console.error("AJAX error:", error);
            }
        });
    }

    function createBarChart(chartId, type, label, data, color, indexAxis = "y") {
        try {
            if (!chartId || !data?.labels || !data?.values) throw new Error('Missing parameters');

            const ctx = document.getElementById(chartId);
            if (!ctx) throw new Error(`Canvas "${chartId}" not found`);

            const existingChart = Chart.getChart(chartId);
            if (existingChart) existingChart.destroy();

            const total = data.values.reduce((sum, value) => sum + value, 0);
            const percentages = data.values.map(v => total > 0 ? Math.round((v / total) * 100) : 0);

            return new Chart(ctx, {
                type: type,
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: label,
                        data: data.values,
                        backgroundColor: Array.isArray(color) ? color : [color],
                        borderWidth: 1,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: indexAxis,
                    scales: {
                        y: { grid: { display: false } },
                        x: { grid: { display: false }, min: 0 }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => `${context.parsed.x || context.parsed.y} (${percentages[context.dataIndex]}%)`
                            }
                        },
                        datalabels: {
                            color: '#000',
                            anchor: 'end',
                            align: 'end',
                            formatter: (value, context) =>
                                `${value} (${percentages[context.dataIndex]}%)`,
                            font: { weight: 'bold', size: 12 }
                        }
                    }
                },
                plugins: [ChartDataLabels]
            });
        } catch (error) {
            console.error('Chart error:', error.message);
        }
    }

    // Run on page load
    fetchEmployeeCountByDepartment();
});
