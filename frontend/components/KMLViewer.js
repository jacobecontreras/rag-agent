class KMLViewer {
    constructor() {
        this.map = null;
        this.vectorSource = null;
        this.vectorLayer = null;
        this.overlay = null;
    }

    init() {
        this.initializeMap();
        this.setupUpload();
        this.setupSearch();
    }

    initializeMap() {
        // Initialize vector source for KML layers
        this.vectorSource = new ol.source.Vector();

        // Create vector layer
        this.vectorLayer = new ol.layer.Vector({
            source: this.vectorSource,
            style: function(feature) {
                return new ol.style.Style({
                    image: new ol.style.Circle({
                        radius: 6,
                        fill: new ol.style.Fill({ color: '#ff6b6b' }),
                        stroke: new ol.style.Stroke({ color: '#ffffff', width: 2 })
                    }),
                    stroke: new ol.style.Stroke({
                        color: '#ff6b6b',
                        width: 3
                    }),
                    fill: new ol.style.Fill({
                        color: 'rgba(255, 107, 107, 0.3)'
                    })
                });
            }
        });

        // Create popup overlay
        this.overlay = new ol.Overlay({
            element: document.createElement('div'),
            positioning: 'bottom-center',
            stopEvent: false,
            className: 'ol-popup'
        });

        // Create map with OpenStreetMap base layer
        this.map = new ol.Map({
            target: 'map',
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.OSM()
                }),
                this.vectorLayer
            ],
            overlays: [this.overlay],
            view: new ol.View({
                center: ol.proj.fromLonLat([0, 0]),
                zoom: 2
            })
        });

        // Add click handler for popups
        this.map.on('click', (evt) => {
            const feature = this.map.forEachFeatureAtPixel(evt.pixel, (feature) => feature);
            if (feature) {
                this.showPopup(feature, evt.coordinate);
            } else {
                this.hidePopup();
            }
        });
    }

    setupUpload() {
        const uploadBtn = document.getElementById('floatingUploadBtn');
        const fileInput = document.getElementById('kmlFileInput');

        // Upload button click
        uploadBtn.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (event) => {
            const files = Array.from(event.target.files);
            this.handleFiles(files);
            fileInput.value = ''; // Reset input
        });
    }

    setupSearch() {
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');

        searchBtn.addEventListener('click', () => {
            this.searchAddress(searchInput.value);
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchAddress(searchInput.value);
            }
        });
    }

    async searchAddress(address) {
        if (!address.trim()) return;

        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`
            );
            const results = await response.json();

            if (results && results.length > 0) {
                const result = results[0];
                const lon = parseFloat(result.lon);
                const lat = parseFloat(result.lat);

                // Center map on the location
                this.map.getView().setCenter(ol.proj.fromLonLat([lon, lat]));
                this.map.getView().setZoom(15);

                // Add a pin for the searched location
                this.addSearchPin(lon, lat, result.display_name);
            } else {
                alert('Location not found');
            }
        } catch (error) {
            console.error('Search error:', error);
            alert('Error searching for location');
        }
    }

    addSearchPin(lon, lat, displayName) {
        const feature = new ol.Feature({
            geometry: new ol.geom.Point(ol.proj.fromLonLat([lon, lat])),
            name: displayName
        });

        feature.setStyle(new ol.style.Style({
            image: new ol.style.Circle({
                radius: 8,
                fill: new ol.style.Fill({ color: '#4285f4' }),
                stroke: new ol.style.Stroke({ color: '#ffffff', width: 2 })
            })
        }));

        this.vectorSource.addFeature(feature);
    }

    handleFiles(files) {
        const kmlFiles = files.filter(file =>
            file.name.toLowerCase().endsWith('.kml') ||
            file.name.toLowerCase().endsWith('.kmz')
        );

        kmlFiles.forEach(file => {
            this.loadKMLFile(file);
        });
    }

    loadKMLFile(file) {
        const reader = new FileReader();

        reader.onload = (e) => {
            try {
                const kmlContent = e.target.result;
                const format = new ol.format.KML({
                    extractStyles: true,
                    showPointNames: false
                });

                const features = format.readFeatures(kmlContent, {
                    featureProjection: 'EPSG:3857'
                });

                if (features.length > 0) {
                    // Add features to the map
                    this.vectorSource.addFeatures(features);

                    // Fit map to the new features
                    this.fitMapToFeatures(features);

                    console.log(`Loaded ${features.length} features from ${file.name}`);
                } else {
                    console.warn(`No features found in ${file.name}`);
                }
            } catch (error) {
                console.error(`Error loading KML file ${file.name}:`, error);
                alert(`Error loading KML file ${file.name}: ${error.message}`);
            }
        };

        reader.onerror = () => {
            console.error(`Error reading file ${file.name}`);
            alert(`Error reading file ${file.name}`);
        };

        reader.readAsText(file);
    }

    fitMapToFeatures(features) {
        if (features.length === 0) return;

        const extent = ol.extent.createEmpty();
        features.forEach(feature => {
            ol.extent.extend(extent, feature.getGeometry().getExtent());
        });

        // Add some padding
        const padding = [50, 50, 50, 50];
        this.map.getView().fit(extent, {
            padding: padding,
            duration: 1000
        });
    }

    showPopup(feature, coordinate) {
        const properties = feature.getProperties();
        let content = '<div class="popup-content">';

        // Show only description
        if (properties.description) {
            content += properties.description;
        } else {
            content += 'No description available';
        }

        content += '</div>';

        this.overlay.getElement().innerHTML = content;
        this.overlay.setPosition(coordinate);
    }

    hidePopup() {
        this.overlay.setPosition(undefined);
    }

    destroy() {
        if (this.map) {
            this.map.setTarget(null);
            this.map = null;
        }
        this.vectorSource = null;
        this.vectorLayer = null;
        this.overlay = null;
    }
}