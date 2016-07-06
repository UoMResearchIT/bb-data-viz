/* Plot the data viz map */
var mapOptions =  { styles: 
[
    {
        "featureType": "administrative",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "color": "#444444"
            }
        ]
    },
    {
        "featureType": "administrative.country",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "administrative.province",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "administrative.locality",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "all",
        "stylers": [
            {
                "color": "#f2f2f2"
            }
        ]
    },
    {
        "featureType": "landscape.man_made",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "all",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "lightness": 45
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "transit",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "all",
        "stylers": [
            {
                "color": "#46bcec"
            },
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#60baef"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            },
            {
                "color": "#ff0000"
            }
        ]
    }
]
	};

function plotMapData() {
	// Set the map
	var map = new google.maps.Map(document.getElementById('bb-mapid'), mapOptions);
	
	var ctaLayer = new google.maps.KmlLayer({
		url: 'http://130.88.198.51/bb/api/symptom_score.kml?nocache='+(new Date()).getTime(),
		map: map
	});
	
	setLoader(0, 'Map load complete.');
}

function setControls() {
	// Bind events for the view buttons
	$('.bb-map-control').click(function() {
		$('.bb-map-control').removeClass('bb-map-control-active');
		$(this).addClass('bb-map-control-active');
		
		var dataFile = $(this).data('kml-file');
		
		setLoader(1, 'Loading data...');
		
		// Set the map
		var map = new google.maps.Map(document.getElementById('bb-mapid'), mapOptions);
		
		var ctaLayer = new google.maps.KmlLayer({
			url: 'http://130.88.198.51/bb/api/'+dataFile+'?nocache='+(new Date()).getTime(),
			map: map
		});
		
		setLoader(0, 'Data load complete.');
	});
}

function setLoader(on, msg) {
	// Set the loading message
	$('#bb-loader-text').text(msg);
	
	if(on) {
		$('#bb-loader').show();
	} else {
		setTimeout(function() {
			$('#bb-loader').hide();
		}, 4000);
	}
}

$(function() {
	setLoader(1, 'Loading map...');
	plotMapData();
	setControls();
});	
