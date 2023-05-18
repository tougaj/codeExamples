import { styled } from 'styled-components';
import { IGridDayData } from './common';

interface ICalendarDateItemProps extends IGridDayData {
	start?: number;
	dayClassName?: string;
}
const CalendarDateItem = ({ date, count, start, dayClassName }: ICalendarDateItemProps) => (
	<GridItem style={{ gridColumn: start }}>
		<DayItem>
			{count ? (
				<button data-day={date} className="calendar__day">
					{date}
				</button>
			) : (
				<span className={dayClassName || 'text-muted'}>{date}</span>
			)}
		</DayItem>
		{count !== undefined && <CountItem className="text-muted">{count || '-'}</CountItem>}
	</GridItem>
);

export default CalendarDateItem;

const GridItem = styled.div`
	display: flex;
	flex-direction: column;
	align-items: center;
	.calendar__week_em {
		color: rgba(255, 0, 0, 0.87);
	}
	button {
		border: none;
		background-color: inherit;
		font-size: inherit;
		color: rgba(120, 120, 255, 0.87);
		cursor: pointer;
	}
`;

const DayItem = styled.span`
	font-size: 1em;
`;

const CountItem = styled.span`
	font-size: 0.6em;
	border-top: 1px solid rgba(255, 255, 255, 0.5);
	width: 100%;
	text-align: center;
`;
