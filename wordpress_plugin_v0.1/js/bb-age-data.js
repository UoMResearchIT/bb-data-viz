// Loop over the data
onmessage = function(e) {
	console.log('Worker started for age chart...');
	
	var data = {};
		data.ageunder18 = 0;
		data.age1830 = 0;
		data.age3140 = 0;
		data.age4150 = 0;
		data.age5160 = 0;
		data.age6170 = 0;
		data.ageover70 = 0;
	
	var i=0;
	for(i; i<e.data.length; i++) {
		var dob = e.data[i]['Year of Birth'];
		var currentYear = new Date().getFullYear();
		
		var age = currentYear-dob;
		
		switch(true) {
			case age < 18:
				data.ageunder18++;
				break;
			case age > 18 && age < 31:
				data.age1830++;
				break;
			case age > 31 && age < 41:
				data.age3140++;
				break;
			case age > 41 && age < 51:
				data.age4150++;
				break;
			case age > 51 && age < 61:
				data.age5160++;
				break;
			case age > 61 && age < 71:
				data.age6170++;
				break;
			case age > 70:
				data.ageover70++;
				break;
		}
	}
	
	console.log(data);
	
	var ageunder18 = ((100*data.ageunder18)/i).toFixed(2);
	var age1830 = ((100*data.age1830)/i).toFixed(2);
	var age3140 = ((100*data.age3140)/i).toFixed(2);
	var age4150 = ((100*data.age4150)/i).toFixed(2);
	var age5160 = ((100*data.age5160)/i).toFixed(2);
	var age6170 = ((100*data.age6170)/i).toFixed(2);
	var ageover70 = ((100*data.ageover70)/i).toFixed(2);
	
	// Send the data back as a percentage
	var dataPercents = {
		'ageunder18': ageunder18,
		'age1830': age1830,
		'age3140': age3140,
		'age4150': age4150,
		'age5160': age5160,
		'age6170': age6170,
		'ageover70': ageover70
	}
	
	postMessage(dataPercents);
}