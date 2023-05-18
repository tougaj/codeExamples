import dayjs from 'dayjs';
import { useEffect, useState } from 'react';
import { styled } from 'styled-components';
import CalendarGrig from './CalendarGrid';
import { YearMonth } from './classes/yearMonth';

interface ICalendarProps {
	strDate: string;
}
const Calendar = ({ strDate }: ICalendarProps) => {
	const [ym, setYm] = useState<YearMonth>(new YearMonth(strDate));

	useEffect(() => {
		setYm(new YearMonth(strDate));
	}, [strDate]);

	const onDayClick = (day: string) => {
		const [year, month] = ym.getYM();
		alert(`${year}-${month.toString().padStart(2, '0')}-${day.padStart(2, '0')}`);
	};

	const [year, month] = ym.getYM();
	return (
		<div>
			<CalendarMonth className="text-center">
				{/* {ym.value.toLocaleDateString('uk-UA', { year: 'numeric', month: 'long' })} */}
				{dayjs(ym.value).format('MMMM YYYY')}
			</CalendarMonth>
			<CalendarGrig
				data={new Array(ym.daysCount()).fill(undefined).map((_, index) => ({
					date: new Date(year, month-1, index + 1).toISOString(),
					count: Math.random() < 0.3 ? 0 : Math.floor(Math.random() * 100),
				}))}
				onDayClick={onDayClick}
				firstDoW={ym.firstDoW() || 7}
			/>
		</div>
	);
};

export default Calendar;

const CalendarMonth = styled.div`
	font-size: 1.25em;
	margin-bottom: 0.25em;
`;
