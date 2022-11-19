import * as dotenv from 'dotenv';
import { getData, getGroupedData, getMeasures, getNumberEnvironmentVariable } from './utils';

dotenv.config();

const PARTS_COUNT = getNumberEnvironmentVariable('PARTS_COUNT', "part's count");
const MAX_FILE_SIZE = getNumberEnvironmentVariable('MAX_FILE_SIZE', 'maximum file size');

const data = getData(MAX_FILE_SIZE);
const totalSize = data.reduce((prev, cur) => prev + cur);
console.log(`Total size is ${totalSize} Mb`);
const partSize = totalSize / PARTS_COUNT;
console.log(`Part size is ${partSize} Mb`);

const groupedData = getGroupedData(data);
// console.log(groupedData);
const measures = getMeasures(PARTS_COUNT, partSize, groupedData);

console.log('Measures', measures);
