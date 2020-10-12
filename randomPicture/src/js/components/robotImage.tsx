import React, { useEffect, useState } from 'react';

interface IRobotImageProps extends React.HTMLAttributes<HTMLDivElement> {
	providerUrl?: string;
	timeoutInterval?: number;
}
const RobotImage = ({ providerUrl = 'https://robohash.org/', timeoutInterval = 5000 }: IRobotImageProps) => {
	const getRandomRobot = () => `${providerUrl}${new Date().valueOf()}?set=set${Math.floor(Math.random() * 4 + 1)}`;

	const [img, setImg] = useState(getRandomRobot());

	useEffect(() => {
		let tm: number | null = null;

		tm = window.setInterval(() => {
			setImg(getRandomRobot());
		}, timeoutInterval);

		return () => {
			if (tm) clearInterval(tm);
		};
	}, []);

	if (!img) return <></>;
	return <img src={img} alt="Робот" className="random-image rounded" />;
};

export default RobotImage;
