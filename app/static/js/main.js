let map;
let markers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById('map-container'), {
        center: {lat: 7.8731, lng: 80.7718},
        zoom: 8
    });

    fetchPlants();
    fetchSubstations();
    fetchForecastLocations();
}

function fetchPlants() {
    fetch('/api/plants')
        .then(response => response.json())
        .then(plants => {
            const plantList = document.getElementById('plant-list');
            plants.forEach(plant => {
                addMarker(plant, 'plant');
                const li = document.createElement('li');
                li.textContent = `${plant.name} (${plant.type})`;
                plantList.appendChild(li);
            });
        });
}

function fetchSubstations() {
    fetch('/api/substations')
        .then(response => response.json())
        .then(substations => {
            const substationList = document.getElementById('substation-list');
            substations.forEach(substation => {
                addMarker(substation, 'substation');
                const li = document.createElement('li');
                li.textContent = substation.name;
                substationList.appendChild(li);
            });
        });
}

function fetchForecastLocations() {
    fetch('/api/forecast_locations')
        .then(response => response.json())
        .then(locations => {
            const locationList = document.getElementById('forecast-location-list');
            locations.forEach(location => {
                addMarker(location, 'forecast');
                const li = document.createElement('li');
                li.textContent = location.name;
                locationList.appendChild(li);
            });
        });
}

function addMarker(item, type) {
    const marker = new google.maps.Marker({
        position: {lat: item.lat, lng: item.lng},
        map: map,
        title: item.name
    });

    marker.addListener('click', () => {
        if (type === 'plant') {
            fetchPlantForecast(item.id);
        } else if (type === 'substation') {
            fetchSubstationForecast(item.id);
        }
    });

    markers.push(marker);
}

function fetchPlantForecast(plantId) {
    fetch(`/api/forecast/${plantId}`)
        .then(response => response.json())
        .then(data => {
            updateForecastChart(data);
        });
}

function fetchSubstationForecast(substationId) {
    fetch(`/api/substation_forecast/${substationId}`)
        .then(response => response.json())
        .then(data => {
            updateSubstationForecastChart(data);
        });
}

function updateForecastChart(data) {
    const ctx = document.getElementById('forecast-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => new Date(d.timestamp).toLocaleString()),
            datasets: [{
                label: 'Forecast',
                data: data.map(d => d.ghi || d.wind_speed || d.precipitation),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour'
                    }
                }
            }
        }
    });
}

function updateSubstationForecastChart(data) {
    const ctx = document.getElementById('forecast-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.solar.map(d => new Date(d.timestamp).toLocaleString()),
            datasets: [
                {
                    label: 'Solar GHI',
                    data: data.solar.map(d => d.avg_ghi),
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                },
                {
                    label: 'Wind Speed',
                    data: data.wind.map(d => d.avg_wind_speed),
                    borderColor: 'rgb(54, 162, 235)',
                    tension: 0.1
                },
                {
                    label: 'Hydro Precipitation',
                    data: data.hydro.