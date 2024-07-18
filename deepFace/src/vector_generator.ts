#!/usr/bin/env node
import { faker } from '@faker-js/faker';
import fs from 'fs';
import { v4 as uuidv4 } from 'uuid';

interface ISolrRecord {
	id: string;
	face: number[];
}

const DIMENSIONS = 4096;
const RECORDS_COUNT = 100000;
const RECORDS_PER_FILE = 2000;
const FILE_TEMPLATE = 'data_';

const saveToFile = (data: ISolrRecord[], fileName: string) => {
	fs.writeFileSync(fileName, JSON.stringify(result, undefined, '  '), 'utf-8');
	// fs.writeFileSync(fileName, JSON.stringify(result), 'utf-8');
	console.log(`Printed ${data.length} records into file ${fileName}`);
};

let fileNo = 0;
let result: ISolrRecord[] = [];
for (let i = 0; i < RECORDS_COUNT; i++) {
	const face: number[] = [];
	for (let j = 0; j < DIMENSIONS; j++) {
		face.push(Math.random() < 0.85 ? 0 : faker.number.float({ min: 0, max: 0.3, fractionDigits: 6 }));
	}
	result.push({ id: uuidv4(), face });
	if ((i + 1) % RECORDS_PER_FILE === 0) {
		saveToFile(result, `local.${FILE_TEMPLATE}${(fileNo++).toString().padStart(3, '0')}.json`);
		result = [];
	}
}

if (result.length !== 0) saveToFile(result, `local.${FILE_TEMPLATE}${(fileNo++).toString().padStart(3, '0')}.json`);
