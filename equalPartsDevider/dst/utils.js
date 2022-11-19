"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getMeasures = exports.getGroupedData = exports.getNumberEnvironmentVariable = exports.getData = exports.Mb = void 0;
const fs_1 = __importDefault(require("fs"));
exports.Mb = 1024 * 1024;
const getData = (maxFileSize) => {
    const data = fs_1.default
        .readFileSync('video.txt', 'utf-8')
        .split('\n')
        .map((strSize) => parseInt(strSize) / exports.Mb)
        .filter((size) => size < maxFileSize);
    data.sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
    return data;
};
exports.getData = getData;
const getNumberEnvironmentVariable = (name, addString) => {
    const envValue = process.env[name];
    if (!envValue) {
        console.log(`eed environment variable ${name} - ${addString}`);
        process.exit(1);
    }
    return parseInt(envValue);
};
exports.getNumberEnvironmentVariable = getNumberEnvironmentVariable;
const getGroupedData = (data) => {
    const dataByMb = {};
    data.forEach((item) => {
        const index = Math.floor(item);
        if (!dataByMb[index])
            dataByMb[index] = [];
        dataByMb[index].push(item);
    });
    const groupedData = [];
    let movingSize = 0;
    Object.entries(dataByMb).forEach(([key, value]) => {
        const sum = value.reduce((prev, cur) => prev + cur);
        movingSize += sum;
        groupedData.push({
            mb: parseInt(key),
            data: value,
            size: sum,
            movingSize,
            count: value.length,
        });
    });
    return groupedData;
};
exports.getGroupedData = getGroupedData;
const getMeasureItem = (maxSize, data, startDataIndex) => {
    let curIndex = startDataIndex;
    for (let index = startDataIndex; index < data.length; index++) {
        if (maxSize < data[index].movingSize)
            break;
        curIndex = index;
    }
    return [curIndex, data[curIndex].mb];
};
const getMeasures = (partsCount, partSize, groupedData) => {
    const partsMeasurers = Array(partsCount)
        .fill(undefined)
        .map((_, index) => (index + 1) * partSize);
    console.log('Parts measures', partsMeasurers);
    const measures = Array(partsCount).fill(0);
    let startDataIndex = 0;
    for (let index = 0; index < partsCount; index++) {
        [startDataIndex, measures[index]] = getMeasureItem(partsMeasurers[index], groupedData, startDataIndex);
    }
    return measures;
};
exports.getMeasures = getMeasures;
