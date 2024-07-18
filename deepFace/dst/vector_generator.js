#!/usr/bin/env node
"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const faker_1 = require("@faker-js/faker");
const fs_1 = __importDefault(require("fs"));
const uuid_1 = require("uuid");
const DIMENSIONS = 4096;
const RECORDS_COUNT = 100000;
const RECORDS_PER_FILE = 2000;
const FILE_TEMPLATE = 'data_';
const saveToFile = (data, fileName) => {
    fs_1.default.writeFileSync(fileName, JSON.stringify(result, undefined, '  '), 'utf-8');
    // fs.writeFileSync(fileName, JSON.stringify(result), 'utf-8');
    console.log(`Printed ${data.length} records into file ${fileName}`);
};
let fileNo = 0;
let result = [];
for (let i = 0; i < RECORDS_COUNT; i++) {
    const face = [];
    for (let j = 0; j < DIMENSIONS; j++) {
        face.push(Math.random() < 0.85 ? 0 : faker_1.faker.number.float({ min: 0, max: 0.3, fractionDigits: 6 }));
    }
    result.push({ id: (0, uuid_1.v4)(), face });
    if ((i + 1) % RECORDS_PER_FILE === 0) {
        saveToFile(result, `local.${FILE_TEMPLATE}${(fileNo++).toString().padStart(3, '0')}.json`);
        result = [];
    }
}
if (result.length !== 0)
    saveToFile(result, `local.${FILE_TEMPLATE}${(fileNo++).toString().padStart(3, '0')}.json`);
