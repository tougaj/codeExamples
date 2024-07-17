#!/usr/bin/env node
import { faker } from '@faker-js/faker';
import { v4 as uuidv4 } from 'uuid';

interface ISolrRecord {
	id: string;
	face: number[];
}

const DIMENSIONS = 4;
const COUNT = 1000;

const result: ISolrRecord[] = [];
for (let i = 0; i < COUNT; i++) {
	const face: number[] = [];
	for (let j = 0; j < DIMENSIONS; j++) {
		face.push(Math.random() < 0.85 ? 0 : faker.number.float({ min: 0, max: 0.3, fractionDigits: 6 }));
	}
	result.push({ id: uuidv4(), face });
}

console.log(JSON.stringify(result, undefined, '  '));
