const parseKMZ = require('parse2-kmz');
import fs from 'fs';
const INPUT_PATH = './input/';
const OUTPUT_PATH = './output/';

const convertKmzToJson = async (baseFilename: string) => {
	try {
		const kmz = await parseKMZ.toJson(`${INPUT_PATH}${baseFilename}`);
		const json = JSON.stringify(kmz, undefined, 2);
		fs.writeFileSync(`${OUTPUT_PATH}${baseFilename}.json`, json);
		console.log(`${baseFilename} converted`);
		return true;
	} catch (error) {
		console.error(`Error converting file ${baseFilename}: ${error}`);
	}
	return false;
};

const convertFiles = async () => {
	const files = fs.readdirSync(INPUT_PATH).filter((file) => file.endsWith('.kmz'));

	await Promise.all(files.map((file) => convertKmzToJson(file)));

	console.log('All files converted');
};

convertFiles();
// convertKmzToJson('Обстановка');
