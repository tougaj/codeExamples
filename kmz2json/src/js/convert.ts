const parseKMZ = require('parse2-kmz');
const fs = require('fs');
const INPUT_PATH = './input/';
const OUTPUT_PATH = './output/';

const convertKmzToJson = async (baseFilename: string) => {
	try {
		const kmz = await parseKMZ.toJson(`${INPUT_PATH}${baseFilename}.kmz`);
		const json = JSON.stringify(kmz, undefined, 2);
		fs.writeFileSync(`${OUTPUT_PATH}${baseFilename}.json`, json);
		console.log('Done');
	} catch (error) {
		console.error(error);
	}
};

convertKmzToJson('Обстановка');
