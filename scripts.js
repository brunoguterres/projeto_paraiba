function onEachFeature(feature, layer) {
    layer.on('click', function (e) {
        var cobaciaValue = feature.properties.cobacia;

        var cobaciaEdit = cobaciaValue;
        while (cobaciaEdit.length > 0 && parseInt(cobaciaEdit.slice(-1)) % 2 !== 0) {
            cobaciaEdit = cobaciaEdit.slice(0, -1); // Remove o último dígito
        };
    
        var popupContent = "CobaciaValue: " + cobaciaValue + "<br>CobaciaEdit: " + cobaciaEdit;
        
        L.popup()
            .setLatLng(e.latlng)
            .setContent(popupContent)
            .openOn(map);
        
        var ottobaciasMontante = L.Geoserver.wfs('http://191.252.221.146:8080/geoserver/wfs', {
            layers: 'teste_shapefile:ottobacias_iguacu_5k',
            fitLayer: false,
            className: 'camada_ottobacias_montante',
            CQL_FILTER: "cobacia LIKE '"+cobaciaEdit+"%' AND cobacia > '"+cobaciaValue+"'"
        });
        ottobaciasMontante.addTo(map);
        
        var ottobaciaSelecionada = L.Geoserver.wfs('http://191.252.221.146:8080/geoserver/wfs', {
            layers: 'teste_shapefile:ottobacias_iguacu_5k',
            fitLayer: false,
            className: 'camada_ottobacias_selecionada',
            CQL_FILTER: "cobacia LIKE '"+cobaciaValue+"'"
        });
        ottobaciaSelecionada.addTo(map);
    });
}

var baseGoogleStreets = L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: 'Google Streets © <a href="https://www.google.com/maps">Google Maps</a>'
});

var baseGoogleSatelite = L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 22,
    attribution: 'Imagem de satélite © <a href="https://www.google.com/maps">Google Maps</a>'
});

var baseOpenStreetMap = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
});

var ottotrechos = L.Geoserver.wfs('http://191.252.221.146:8080/geoserver/wfs', {
    layers: 'teste_shapefile:ottotrechos_iguacu_5k',
    //className: 'camada_ottobacias',
    attribution: 'ANA',
    //CQL_FILTER: "cobacia LIKE '86288%'",
    //onEachFeature: onEachFeature
});

var ottobacias = L.Geoserver.wfs('http://191.252.221.146:8080/geoserver/wfs', {
    layers: 'teste_shapefile:ottobacias_iguacu_5k',
    className: 'camada_ottobacias',
    attribution: 'ANA',
    CQL_FILTER: "cobacia LIKE '8628%'",
    onEachFeature: onEachFeature
});

var map = L.map('map', {
    center: [-15, -51.5],
    zoom: 4,
    layers: [baseGoogleStreets, ottobacias]
});

var baseMaps = {
    "Google Streets": baseGoogleStreets,
    "Google Satelite": baseGoogleSatelite,
    "OpenStreetMap": baseOpenStreetMap    
};

var overlayMaps = {
    "Ottobacias": ottobacias,
    "Ottotrechos": ottotrechos
};

var layerControl = L.control.layers(baseMaps, overlayMaps);

layerControl.addTo(map);