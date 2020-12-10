/// <reference path="../globals.d.ts" />

import React, { useState } from 'react';
import { RandomizeNodePositions, RelativeSize, Sigma } from 'react-sigma';
import DragNodes from 'react-sigma/lib/DragNodes';
import ForceLink from 'react-sigma/lib/ForceLink';
// import NOverlap from 'react-sigma/lib/ForceLink';

interface ISchemeProps extends React.AllHTMLAttributes<HTMLDivElement> {}
const Scheme = ({}: ISchemeProps) => {
	// "line" | "arrow" | "curve" | "curvedArrow" | "dashed" | "dotted" | "parallel" | "tapered"
	const [graph, setGraph] = useState<unknown | undefined>(myGraph1);
	const [ts, setTs] = useState(0);

	const onChangeGraph = () => {
		setGraph(graph === myGraph1 ? myGraph2 : myGraph1);
		setTs(new Date().valueOf());
	};

	return (
		<>
			<Sigma
				key={ts}
				graph={graph}
				settings={{
					// drawEdges: true,
					// drawEdgeLabels: true,
					clone: false,
					labelThreshold: 1,
					defaultNodeType: 'circle',
					defaultEdgeType: 'tapered',
					minNodeSize: 2,
					maxNodeSize: 15,
					// minEdgeSize: 0.5,
					// maxEdgeSize: 1,
					// enableEdgeHovering: true,
					// edgeHoverSizeRatio: 2,
				}}
				style={{ maxWidth: 'inherit', height: '100%' }}
				renderer="canvas"
			>
				{/* <EdgeShapes default="tapered" /> */}
				{/* <NodeShapes default="circle" /> */}
				<RandomizeNodePositions />
				<DragNodes />
				<RelativeSize initialSize={2} />
				{/* <NOverlap timeout={3000} duration={1000} /> */}
				<ForceLink
					timeout={3000}
					easing="cubicInOut"
					scalingRatio={10}
					alignNodeSiblings
					barnesHutOptimize
					barnesHutTheta={0.6}
					iterationsPerRender={10}
				/>
			</Sigma>
			<button onClick={onChangeGraph}>Змінити</button>
		</>
	);
};

export default Scheme;

// console.log(SigmaEnableWebGL);
// console.log(SigmaEnableSVG);

const myGraph1 = {
	nodes: [
		{
			id: 'n1',
			label: 'Alice',
			// borderColor: 'yellow',
			color: 'rgba(0,0,255,0.5)',
			image: {
				url: '1.jpg',
				scale: 1.4142135623730951,
			},
		},
		{ id: 'n2', label: 'Rabbit' },
		{ id: 'n3', label: 'Шляпник' },
		{
			id: 'n4',
			label: 'Queen',
			color: 'rgba(0,0,255,0.5)',
			image: {
				url: '1.jpg',
				scale: 1.4142135623730951,
			},
		},
		{
			id: 'n5',
			label: 'King',
			image: {
				url: '1.jpg',
				scale: 1.4142135623730951,
			},
		},
		{ id: 'n6', label: 'Queen2' },
		{ id: 'n7', label: 'Кот' },
		{ id: 'n8', label: 'Кот' },
		{ id: 'n9', label: 'Кот' },
		{ id: 'n10', label: 'Кот' },
		{ id: 'n11', label: 'Кот' },
		{ id: 'n12', label: 'Кот' },
	],
	edges: [
		{ id: 'e1', source: 'n1', target: 'n2', label: 'SEES' },
		{ id: 'e2', source: 'n1', target: 'n3', label: 'SEES' },
		{ id: 'e3', source: 'n1', target: 'n4', label: 'bla' },
		{ id: 'e4', source: 'n4', target: 'n5', label: 'bla' },
		{ id: 'e5', source: 'n4', target: 'n6', label: 'bla' },
		{ id: 'e6', source: 'n1', target: 'n7', label: 'SEES', color: 'rgba(0,127,0,0.5)' },
		{ id: 'e7', source: 'n7', target: 'n8', label: 'bla' },
		{ id: 'e8', source: 'n8', target: 'n9', label: 'bla' },
		{ id: 'e9', source: 'n4', target: 'n9', label: 'bla' },
		{ id: 'e10', source: 'n4', target: 'n8', label: 'bla' },
		{ id: 'e11', source: 'n8', target: 'n10', label: 'bla' },
		{ id: 'e12', source: 'n8', target: 'n11', label: 'bla' },
		{ id: 'e13', source: 'n11', target: 'n12', label: 'bla' },
	],
};

const myGraph2 = {
	nodes: [
		{
			id: 'n1',
			label: 'Alice',
			// borderColor: 'yellow',
			color: 'rgba(0,0,255,0.5)',
			image: {
				url: '1.jpg',
				scale: 1.4142135623730951,
			},
		},
		{ id: 'n2', label: 'Rabbit' },
		{ id: 'n3', label: 'Шляпник' },
		{
			id: 'n4',
			label: 'Queen',
			color: 'rgba(0,0,255,0.5)',
			image: {
				url: '1.jpg',
				scale: 1.4142135623730951,
			},
		},
	],
	edges: [
		{ id: 'e1', source: 'n1', target: 'n2', label: 'SEES' },
		{ id: 'e2', source: 'n1', target: 'n3', label: 'SEES' },
		{ id: 'e3', source: 'n1', target: 'n4', label: 'bla' },
	],
};
