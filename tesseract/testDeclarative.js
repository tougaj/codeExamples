const Tesseract = require('tesseract.js');

const recognizeFile = async (fileName, language) => {
	const startTime = new Date().getTime();

	const { text, duration } = await Tesseract.recognize(fileName, language, { logger: (m) => console.log(m) }).then(
		({ data: { text } }) => {
			return {
				text,
				duration: new Date().getTime() - startTime,
			};
		}
	);
	console.log(text);
	console.log(`Duration: ${duration / 1000} ms`);
};

!(async () => {
	await recognizeFile('./input/u1.png', 'ukr');
	await recognizeFile('./input/u2.png', 'ukr');
})();
