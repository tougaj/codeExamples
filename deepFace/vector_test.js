#!/usr/bin/env node

const { sources, target } = require('./local.data.js');

const result = [];

const getEuclidDistance = (a, b) => {
	sum = 0;
	for (let index = 0; index < a.length; index++) {
		sum += (a[index] - b[index]) * (a[index] - b[index]);
	}
	return Math.sqrt(sum);
};

for (const key in sources) {
	// let zeros = 0;
	// for (item of sources[key]){
	// 	if (item === 0.0) zeros++;
	// }
	// console.log(`Zeros count: ${zeros}`);
	// console.log(new Set(sources[key]));
	// console.log(`Min: ${Math.min(...sources[key])}, Max: ${Math.max(...sources[key])}`);
	result.push({ key, distance: getEuclidDistance(sources[key], target) });
}
result.sort((a, b) => a.distance - b.distance);

console.log(result);
