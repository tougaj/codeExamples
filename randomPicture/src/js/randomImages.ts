interface IPicResponse {
	file: string;
}

const updateImage = (imgFileName: string, rounded = false) => {
	const img: HTMLImageElement = document.querySelector('.random-image') as HTMLImageElement;
	img.src = imgFileName;
	if (rounded) img.classList.add('rounded');
	else img.classList.remove('rounded');
};

export const loadImageFromRobohash = () => {
	updateImage(`https://robohash.org/${new Date().valueOf()}?set=set4`);
	// const url = `https://robohash.org/${new Date().valueOf()}?set=set4`;
};

export const loadImageFromMeow = () => {
	const url = 'https://aws.random.cat/meow';
	fetch(url)
		.then((response) => response.json())
		.then((r: IPicResponse) => updateImage(r.file, true))
		.catch(alert);
};
