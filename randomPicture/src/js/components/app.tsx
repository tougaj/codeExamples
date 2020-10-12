import React, { useState } from 'react';
import CatImage from './catImage';
import RobotImage from './robotImage';

interface IAppProps {}
export const App = (props: IAppProps) => {
	const [activeKey, setActiveKey] = useState('list');

	const onTabSelect = (newActiveKey: string) => {
		setActiveKey(newActiveKey);
	};

	return (
		<div className="row">
			<div className="col">
				<CatImage />
			</div>
			<div className="col">
				<RobotImage timeoutInterval={4000} />
			</div>
		</div>
	);
};
