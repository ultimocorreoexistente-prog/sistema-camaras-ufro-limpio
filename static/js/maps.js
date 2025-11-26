// Integración de Leaflet.js para mapas de geolocalización
(function() {
    'use strict';
    
    // Verificar si estamos en página de mapa
    if (!document.getElementById('map')) return;
    
    // Configuración inicial
    const DEFAULT_CENTER = [-38.7359, -72.5904]; // Temuco, Chile
    const DEFAULT_ZOOM = 13;
    
    // Inicializar mapa
    const map = L.map('map').setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    
    // Agregar capa de tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Función para agregar marcadores
    function addMarker(lat, lng, title, description, color = 'blue') {
        if (!lat || !lng) return;
        
        const iconUrl = `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`;
        
        const customIcon = L.icon({
            iconUrl: iconUrl,
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        const marker = L.marker([lat, lng], { icon: customIcon }).addTo(map);
        marker.bindPopup(`<strong>${title}</strong><br>${description}`);
        
        return marker;
    }
    
    // Exportar funciones
    window.LeafletUtils = {
        map: map,
        addMarker: addMarker
    };
    
})();
