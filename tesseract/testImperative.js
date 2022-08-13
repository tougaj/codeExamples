const Tesseract = require('tesseract.js');
const fs = require('fs');
const path = require('path');

const workers = {};

const getWorker = async (language) => {
	if (!workers[language]) {
		const worker = Tesseract.createWorker({ logger: (m) => console.log(m) });
		await worker.load();
		await worker.loadLanguage(language);
		await worker.initialize(language);
		workers[language] = worker;
	}
	return workers[language];
};

const recognizeFile = async (fileName, language) => {
	console.log(`Recognizing ${fileName}`);

	const startTime = new Date().getTime();

	let worker = undefined;
	try {
		worker = await getWorker(language);
	} catch (error) {
		console.log('Error creating worker');
		return;
	}

	const {
		data: { text },
	} = await worker.recognize(fileName);
	console.log(text);
	console.log(`Duration: ${(new Date().getTime() - startTime) / 1000} ms`);
};

const getImages = (dir) => {
	const images = [];
	const files = fs.readdirSync(dir);
	files.forEach((file) => {
		const filePath = path.join(dir, file);
		const stat = fs.statSync(filePath);
		if (stat.isFile()) {
			images.push(filePath);
		}
	});
	return images;
};

!(async () => {
	const images = getImages('./input');

	for (const image of images) {
		await recognizeFile(image, 'ukr');
	}
	// console.log(images);
	// await recognizeFile('./input/u0.png', 'ukr');
	// await recognizeFile('./input/u1.png', 'ukr');
	// await recognizeFile('./input/u2.png', 'ukr');
	// await recognizeFile('./input/u3.png', 'ukr');

	for (const worker of Object.values(workers)) {
		await worker.terminate();
	}
})();
