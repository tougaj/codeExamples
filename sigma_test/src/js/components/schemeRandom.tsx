/// <reference path="../globals.d.ts" />

import React, { useEffect, useState } from 'react';
import { RandomizeNodePositions, RelativeSize, Sigma } from 'react-sigma';
import DragNodes from 'react-sigma/lib/DragNodes';
import ForceLink from 'react-sigma/lib/ForceLink';

// import NOverlap from 'react-sigma/lib/ForceLink';

const COLORS = [
	'rgba(200,0,0,0.67)',
	'rgba(0,200,0,0.67)',
	'rgba(0,0,200,0.67)',
	'rgba(0,200,200,0.67)',
	'rgba(200,0,200,0.67)',
	'rgba(200,200,0,0.67)',
];

interface ISchemeRandomProps extends React.AllHTMLAttributes<HTMLDivElement> {}
const SchemeRandom = ({}: ISchemeRandomProps) => {
	// "line" | "arrow" | "curve" | "curvedArrow" | "dashed" | "dotted" | "parallel" | "tapered"
	const [graph, setGraph] = useState<unknown | undefined>();
	const [ts, setTs] = useState(0);

	const getNode = (id: number) => {
		return {
			id,
			label: `Node ${id}`,
			borderColor: 'rgba(64,64,64,0.5)',
			// color: 'rgba(127,127,127,0.5)',
			color: 'white',
			// image: {
			// 	url: '1.jpg',
			// 	scale: 1.4142135623730951,
			// },
		};
	};

	const getEdge = (id: number, nodeLength: number) => {
		const n1 = Math.floor(Math.random() * nodeLength);
		const n2 = Math.floor(Math.random() * nodeLength);

		if (n1 === n2) return;
		return {
			id: `e${id}`,
			source: n1,
			target: n2,
			label: `${n1} = ${n2}`,
			color: COLORS[Math.floor(Math.random() * COLORS.length)],
		};
	};

	useEffect(() => {
		const NODE_COUNTS = 100;
		if (graph !== undefined) return;
		const nodes: any[] = [];
		for (let index = 0; index < NODE_COUNTS; index++) {
			nodes.push(getNode(index));
		}

		const nodeLength = nodes.length;

		const edges: any = [];
		for (let index = 0; index < NODE_COUNTS * 1; index++) {
			const newEdge = getEdge(index, nodeLength);
			if (newEdge === undefined) continue;
			edges.push(newEdge);
        }

		setGraph({
			nodes,
			edges,
		});
		setTs(new Date().valueOf());
	}, [graph]);

	const refresh = () => setGraph(undefined);

	return (
		<>
			<Sigma
				key={ts}
				graph={graph}
				settings={{
					// drawEdges: true,
					// drawEdgeLabels: true,
					clone: false,
					// labelThreshold: 1,
					labelThreshold: 11,
					defaultNodeType: 'circle',
					defaultEdgeType: 'tapered',
					minNodeSize: 2,
					maxNodeSize: 5,
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
					// scalingRatio={1000}
					alignNodeSiblings
					barnesHutOptimize
					barnesHutTheta={0.6}
					iterationsPerRender={10}
				/>
			</Sigma>
			<button onClick={refresh}>Refresh</button>
		</>
	);
};

export default SchemeRandom;

// console.log(SigmaEnableWebGL);
// console.log(SigmaEnableSVG);
