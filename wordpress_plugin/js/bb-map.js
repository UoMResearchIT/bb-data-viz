/* Plot the data viz map */

// Fetch the data
(function($) {
	$.getJSON("http://130.88.198.51/bb/api/bb.json", function(data) {
		// Build the map
		var mymap = L.map('bb-mapid').setView([51.505, -0.09], 13);	
		
		console.log(data);
		
		// Parse data onto the map
		
		// Parse groupings keys
		
		
	});
}(jQuery));
