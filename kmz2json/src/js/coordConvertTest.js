const coord = require('coordinate-formats')
// const coordinatesString = "47º 26' 34.6'' N 33º 41' 42.2'' E";
const coordinatesString = "47º26'34.6''N 33º41'42.2''E";
const cleanedString = coordinatesString.replace(/[^\d.NSWE]/ig, ' ');
console.log(cleanedString);

// const parsedCoordinats = coordinates.map(s => coord.parsePossibleCoordinates(s)[0].toLatLonObject())
	// .map(({latitude, longitude}) => console.log(`${longitude} ${latitude},`));

// console.log(parsedCoordinats);

// parse coordinates
const possibleCoordinates = coord.parsePossibleCoordinates(cleanedString);

console.log(possibleCoordinates);
if (possibleCoordinates.lehgth !== 0){
	console.log(possibleCoordinates[0].toLatLonObject());
	console.log(possibleCoordinates[0].toString());
	
}

// format coordinates
// const coordinates = possibleCoordinates[0];
// const coordinatesFormatted = coordinates.toString();