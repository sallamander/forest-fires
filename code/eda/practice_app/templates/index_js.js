var api_key = '{{api_key | safe}}'
L.mapbox.accessToken = api_key;
var map = L.mapbox.map('map', 'mapbox.streets')
    .setView([30.25, -97.75], 7);