import * as fs from 'fs';

interface IGroupedData {
	mb: number;
	data: number[];
	size: number;
	movingSize: number;
	count: number;
}

export const Mb = 1024 * 1024;

export const getData = (maxFileSize: number) => {
	const data: number[] = fs
		.readFileSync('video.txt', 'utf-8')
		.split('\n')
		.map((strSize) => parseInt(strSize) / Mb)
		.filter((size) => size < maxFileSize);
	data.sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
	return data;
};

export const getNumberEnvironmentVariable = (name: string, addString: string) => {
	const envValue = process.env[name];
	if (!envValue) {
		console.log(`eed environment variable ${name} - ${addString}`);
		process.exit(1);
	}
	return parseInt(envValue);
};

export const getGroupedData = (data: number[]) => {
	const dataByMb: { [key: number]: number[] } = {};
	data.forEach((item) => {
		const index = Math.floor(item);
		if (!dataByMb[index]) dataByMb[index] = [];
		dataByMb[index].push(item);
	});
	const groupedData: IGroupedData[] = [];
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

const getMeasureItem = (desiredTopMeasure: number, data: IGroupedData[], startDataIndex: number) => {
	let curIndex = startDataIndex;
	let deviation = Infinity;
	for (let index = startDataIndex; index < data.length; index++) {
		const newDeviation = data[index].movingSize - desiredTopMeasure;
		if (Math.abs(deviation) < Math.abs(newDeviation)) break;
		// if (desiredTopMeasure < data[index].movingSize) break;
		deviation = newDeviation;
		curIndex = index;
	}
	return [curIndex, data[curIndex].mb, data[curIndex].movingSize, deviation];
};

export const getMeasures = (partsCount: number, partSize: number, groupedData: IGroupedData[]) => {
	const partsMeasurers = Array(partsCount)
		.fill(undefined)
		.map((_, index) => (index + 1) * partSize);
	// console.log('Parts measures', partsMeasurers);

	const measures = Array(partsCount).fill(0);
	const capacity = Array(partsCount).fill(0);
	const deviation = Array(partsCount).fill(0);
	let startDataIndex = 0;
	for (let index = 0; index < partsCount; index++) {
		[startDataIndex, measures[index], capacity[index], deviation[index]] = getMeasureItem(
			partsMeasurers[index],
			groupedData,
			startDataIndex
		);
	}
	for (let index = capacity.length - 1; 0 < index; index--) {
		capacity[index] = capacity[index] - capacity[index - 1];
	}
	return [measures, capacity, deviation];
};
