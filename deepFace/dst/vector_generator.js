#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const faker_1 = require("@faker-js/faker");
const uuid_1 = require("uuid");
const DIMENSIONS = 4;
const COUNT = 1000;
const result = [];
for (let i = 0; i < COUNT; i++) {
    const face = [];
    for (let j = 0; j < DIMENSIONS; j++) {
        face.push(Math.random() < 0.85 ? 0 : faker_1.faker.number.float({ min: 0, max: 0.3, fractionDigits: 6 }));
    }
    result.push({ id: (0, uuid_1.v4)(), face });
}
console.log(JSON.stringify(result, undefined, '  '));
