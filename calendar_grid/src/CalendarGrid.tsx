import dayjs from 'dayjs';
import React from 'react';
import { styled } from 'styled-components';
import CalendarDateItem from './CalendarDateItem';
import { IGridDayData, rotateArrayLeft } from './common';

interface ICalendarGrigProps {
	firstDoW: number;
	data: IGridDayData[];
	onDayClick?: (day: string) => void;
}
const CalendarGrig = ({ firstDoW, data, onDayClick }: ICalendarGrigProps) => {
	const onClick = (event: React.MouseEvent<HTMLElement>) => {
		const element = (event.target as HTMLElement).closest('.calendar__day') as HTMLElement;
		if (!element) return;
		event.preventDefault();
		event.stopPropagation();
		const { day } = element.dataset;
		if (!day) return;
		if (onDayClick) onDayClick(day);
	};

	return (
		<Grid onClick={onClick}>
			<CalendarWeek />
			{data.map(({ date, count }, index) => (
				<CalendarDateItem
					key={date}
					date={new Date(date).getDate().toString()}
					count={count}
					start={index === 0 ? firstDoW : undefined}
				/>
			))}
		</Grid>
	);
};

export default CalendarGrig;

const Grid = styled.div`
	width: 400px;
	border: 1px solid white;
	padding: 0.5em;
	display: grid;
	grid-template-columns: repeat(7, 1fr);
	grid-auto-flow: row;
	gap: 0.5em 1em;
	font-size: 20px;
`;

const CalendarWeek = () => (
	<>
		{rotateArrayLeft<string>([...dayjs.weekdaysMin()]).map((dow, index) => (
			<CalendarDateItem
				key={dow}
				date={dow}
				dayClassName={`calendar__week${4 < index ? ' calendar__week_em' : ''}`}
			/>
		))}
	</>
);
