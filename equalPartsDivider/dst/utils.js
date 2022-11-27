"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getMeasures = exports.getGroupedData = exports.getNumberEnvironmentVariable = exports.getData = exports.Mb = void 0;
const fs = __importStar(require("fs"));
exports.Mb = 1024 * 1024;
const getData = (maxFileSize) => {
    const data = fs
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
const getMeasureItem = (desiredTopMeasure, data, startDataIndex) => {
    let curIndex = startDataIndex;
    let deviation = Infinity;
    for (let index = startDataIndex; index < data.length; index++) {
        const newDeviation = data[index].movingSize - desiredTopMeasure;
        if (Math.abs(deviation) < Math.abs(newDeviation))
            break;
        // if (desiredTopMeasure < data[index].movingSize) break;
        deviation = newDeviation;
        curIndex = index;
    }
    return [curIndex, data[curIndex].mb, data[curIndex].movingSize, deviation];
};
const getMeasures = (partsCount, partSize, groupedData) => {
    const partsMeasurers = Array(partsCount)
        .fill(undefined)
        .map((_, index) => (index + 1) * partSize);
    // console.log('Parts measures', partsMeasurers);
    const measures = Array(partsCount).fill(0);
    const capacity = Array(partsCount).fill(0);
    const deviation = Array(partsCount).fill(0);
    let startDataIndex = 0;
    for (let index = 0; index < partsCount; index++) {
        [startDataIndex, measures[index], capacity[index], deviation[index]] = getMeasureItem(partsMeasurers[index], groupedData, startDataIndex);
    }
    for (let index = capacity.length - 1; 0 < index; index--) {
        capacity[index] = capacity[index] - capacity[index - 1];
    }
    return [measures, capacity, deviation];
};
exports.getMeasures = getMeasures;
//# sourceMappingURL=utils.js.map