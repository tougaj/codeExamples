const { createWorker, createScheduler } = require('tesseract.js');
const fs = require('fs');
const path = require('path');
const gm = require('gm');
require('dotenv').config();

const progressFunction = () => {
	let oldValue = 0;
	return (m) => {
		const newValue = Math.floor(m.progress * 100);
		const printProgress = 5 <= Math.abs(newValue - oldValue) || newValue === 100;
		if (printProgress) {
			oldValue = newValue;
			console.log(`[${m.userJobId}]: ${m.status} ${newValue} %`);
		}
	};
};

const getWorker = async (lang) => {
	const worker = createWorker({
		logger: progressFunction(),
	});
	await worker.load();
	await worker.loadLanguage(lang);
	await worker.initialize(lang);
	return worker;
};

const workersInit = async (scheduler, lang) => {
	const workersPerLanguage = parseInt(process.env.WORKERS_COUNT || '2', 10);
	if (5 <= workersPerLanguage) workersPerLanguage = 5;
	for (let index = 0; index < workersPerLanguage; index++) {
		const worker = await getWorker(lang);
		scheduler.addWorker(worker);
	}
};

const schedulersInit = async (languages) => {
	const schedulers = [];
	for (const lang of languages) {
		console.log(lang);
		const scheduler = createScheduler();
		await workersInit(scheduler, lang);
		schedulers.push(scheduler);
	}
	return schedulers;
};

const getImageLikeObject = async (fileName) => {
	const IMAGE_THRESHOLD = process.env.THRESHOLD || 80;
	const base64 = fs.readFileSync(fileName, 'base64');
	const buffer = Buffer.from(base64, 'base64');
	const baseName = path.basename(fileName);

	gm(buffer, baseName).identify(function (err, data) {
		if (!err) console.log(data.size);
	});

	return new Promise((resolve, reject) => {
		// Сюди можна напряму передавати шлях до файлу зображення fileName.
		// Транслювання з base64 було необхідно для одного з проектів. Тож це тест.
		// gm(fileName)
		gm(buffer, baseName)
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

const recognizeFiles = async (scheduler, fileList) => {
	const results = await Promise.all(
		fileList.map(async (fileName) => {
			return scheduler.addJob('recognize', await getImageLikeObject(fileName));
		})
	);
	return results.map((r) => {
		const text = r.data.text;
		const finalText = text.replace(/\n+/g, ' ');
		const spaceFactor = 1 - finalText.split(/ +/).join('').length / (finalText.length || 1);
		return spaceFactor < process.env.MAX_SPACE_FACTOR ? finalText : undefined;
	});
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
	const languages = process.env.LANGUAGES.split(',').map((s) => s.trim());
	const schedulers = await schedulersInit(languages);

	const images = getImageList(process.env.IMAGES_DIR || './input');

	console.time('🏁 All Done!');
	const results = await Promise.all(schedulers.map((scheduler) => recognizeFiles(scheduler, images)));
	console.log(results);
	console.timeEnd('🏁 All Done!');

	for (const scheduler of schedulers) {
		await scheduler.terminate();
	}
})();
