import * as dotenv from 'dotenv';
import { getData, getGroupedData, getMeasures, getNumberEnvironmentVariable } from './utils';

dotenv.config();

console.log('\nВміст файлу video.txt може бути отриманий за допомогою команди,\nяку необхідно запускати в каталозі video:\nfind -type f -exec stat -c %s {} \\; > ../video.txt\n')


const PARTS_COUNT = getNumberEnvironmentVariable('PARTS_COUNT', "part's count");
const MAX_FILE_SIZE = getNumberEnvironmentVariable('MAX_FILE_SIZE', 'maximum file size');

const data = getData(MAX_FILE_SIZE);
const totalSize = data.reduce((prev, cur) => prev + cur);
console.log(`Total size is ${totalSize.toFixed(1)} Mb`);
const partSize = totalSize / PARTS_COUNT;
console.log(`Part size is ${partSize.toFixed(1)} Mb`);

const groupedData = getGroupedData(data);
// console.log(groupedData);
const [measures, capacity, deviation] = getMeasures(PARTS_COUNT, partSize, groupedData);

console.log('Measures', measures);
console.log('Capacity', capacity.map(Math.round));
console.log('Deviation', deviation.map(Math.round));
