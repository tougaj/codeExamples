import React, { useEffect, useState } from 'react';

interface IPicResponse {
	file: string;
}

interface ICatImageProps extends React.HTMLAttributes<HTMLDivElement> {
	providerUrl?: string;
	timeoutInterval?: number;
}
const CatImage = ({ providerUrl = 'https://aws.random.cat/meow', timeoutInterval = 5000 }: ICatImageProps) => {
	const [img, setImg] = useState<string | null>(null);

	useEffect(() => {
		let tm: number | null = null;

		const loadImage = () => {
			fetch(providerUrl)
				.then((response) => response.json())
				.then((r: IPicResponse) => setImg(r.file))
				.catch(console.log);
		};

		loadImage();
		tm = window.setInterval(() => {
			loadImage();
		}, timeoutInterval);

		return () => {
			if (tm) clearInterval(tm);
		};
	}, []);

	if (!img) return <></>;
	return <img src={img} alt="Котик" className="random-image rounded" />;
};

export default CatImage;
