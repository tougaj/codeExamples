import React from 'react';
import SchemeRandom from './schemeRandom';

interface IAppProps extends React.AllHTMLAttributes<HTMLDivElement> {}
const App = ({}: IAppProps) => {
	return (
		<div className="diagram">
			<SchemeRandom />
		</div>
	);
};

export default App;
