// Fetch data from the backend and render the table and charts
fetch('/data')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }

        // Populate the table
        const tableBody = document.querySelector('#data-table tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            Object.values(row).forEach(cellValue => {
                const td = document.createElement('td');
                td.textContent = cellValue;
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });

        // Prepare data for charts
        const timestamps = data.map(row => row.timestamp);
        const ppmInlet = data.map(row => row.ppm_inlet);
        const co2Inlet = data.map(row => row.co2_inlet);
        const tempInlet = data.map(row => row.temp_inlet);

        // Create PPM Inlet Chart
        new Chart(document.getElementById('ppmInletChart'), {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'PPM Inlet',
                    data: ppmInlet,
                    borderColor: 'blue',
                    fill: false
                }]
            },
            options: { responsive: true }
        });

        // Create CO2 Inlet Chart
        new Chart(document.getElementById('co2InletChart'), {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'CO2 Inlet',
                    data: co2Inlet,
                    borderColor: 'green',
                    fill: false
                }]
            },
            options: { responsive: true }
        });

        // Create Temperature Inlet Chart
        new Chart(document.getElementById('tempInletChart'), {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Temperature Inlet',
                    data: tempInlet,
                    borderColor: 'red',
                    fill: false
                }]
            },
            options: { responsive: true }
        });
    })
    .catch(error => console.error('Error fetching data:', error));
