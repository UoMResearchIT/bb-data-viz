// Loop over the data
onmessage = function(e) {
	console.log('Worker started for gender chart...');
	
	e.data.male = 0;
	e.data.female = 0;
	
	var i=0;
	for(i; i<e.data.length; i++) {
		// Add up the genders
		if(e.data[i]['Gender'] == 'MALE') {
			e.data.male++;
		}
		
		if(e.data[i]['Gender'] == 'FEMALE') {
			e.data.female++;
		}
	}
	
	var male = ((100*e.data.male)/i).toFixed(2);
	var female = ((100*e.data.female)/i).toFixed(2);
	
	// Send the data back as a percentage
	var data = {
		'male': male,
		'female': female
	};
	
	postMessage(data);
}