const Tesseract = require('tesseract.js');
const fs = require('fs');
const path = require('path');
const gm = require('gm');
require('dotenv').config();

const workers = {};

const progressFunction = (m) => {
	console.log(`[${m.userJobId}]: ${m.status} ${(m.progress * 100).toFixed(1)} %`);
};

const getWorker = async (language) => {
	if (!workers[language]) {
		const worker = Tesseract.createWorker({
			logger: progressFunction,
		});
		await worker.load();
		await worker.loadLanguage(language);
		await worker.initialize(language);
		workers[language] = worker;
	}
	return workers[language];
};

const getImageLikeObject = async (fileName) => {
	const IMAGE_THRESHOLD = process.env.THRESHOLD || 80;

	return new Promise((resolve, reject) => {
		gm(fileName)
			.threshold(IMAGE_THRESHOLD, true)
			.toBuffer('PNG', function (err, buffer) {
				// console.log(buffer);
				if (err) reject(err);
				// fs.writeFileSync(`/home/tougaj/code/git/codeExamples/tesseract/u${IMAGE_THRESHOLD}.png`, buffer);
				resolve(buffer);
			});
	});

	// const base64Buffer = fs.readFileSync(fileName, 'base64');
	// return `data:image/png;base64,${base64Buffer}`;

	// const buffer = fs.readFileSync(fileName);
	// return buffer;
};

const recognizeFile = async (fileName, language) => {
	const timeLabel = `⌚ ${fileName} (${language})`;
	console.log(`Recognizing ${fileName}`);
	console.time(timeLabel);

	let worker = undefined;
	try {
		worker = await getWorker(language);
	} catch (error) {
		console.log('Error creating worker');
		return;
	}

	const image = await getImageLikeObject(fileName);
	const {
		data: { text },
	} = await worker.recognize(image);

	const finalText = text.replace(/\n+/g, ' ');
	const spaceFactor = 1 - finalText.split(/ +/).join('').length / (finalText.length || 1);

	console.log('<<<' + finalText + '>>>');
	console.log(spaceFactor);
	if (spaceFactor < process.env.MAX_SPACE_FACTOR) console.log('🟢 Зображення розпізнане');
	else console.warn('🟡 Зображення не містить даних');
	console.timeEnd(timeLabel);
};

const getImageList = (imagesDir) => {
	const images = [];
	const files = fs.readdirSync(imagesDir);
	files.forEach((file) => {
		const filePath = path.join(imagesDir, file);
		const stat = fs.statSync(filePath);
		if (stat.isFile()) {
			images.push(filePath);
		}
	});
	return images;
};

!(async () => {
	const images = getImageList(process.env.IMAGES_DIR || './input');
	const targetLanguage = process.env.TARGET_LANGUAGE || 'ukr';

	console.time('🏁 All Done!');
	for (const image of images) {
		await recognizeFile(image, targetLanguage);
	}

	console.timeEnd('🏁 All Done!');

	for (const worker of Object.values(workers)) {
		await worker.terminate();
	}
})();
