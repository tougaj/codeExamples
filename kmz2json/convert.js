const parseKMZ = require('parse2-kmz');
const fs = require('fs');

const convertKmzToJson = async (baseFilename) => {
	try {
		const kmz = await parseKMZ.toJson(`./input/${baseFilename}.kmz`);
		const json = JSON.stringify(kmz, undefined, 2);
		fs.writeFileSync(`./output/${baseFilename}.json`, json);
		console.log('Done');
	} catch (error) {
		console.error(error);
	}
};

convertKmzToJson('Обстановка');
