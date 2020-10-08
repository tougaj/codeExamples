import moment from 'moment';

interface IHitDate {
	m: moment.Moment;
	dt: string;
}

moment.locale('uk-UA');

document.addEventListener('DOMContentLoaded', () => {
	const dates: IHitDate[] = fillDates();

	const container = document.querySelector('.container');
	if (!container) return;

	fillTable(dates, container);
});

function fillDates() {
	const curDate = moment();
	const dates: IHitDate[] = [];
	const date = moment().subtract(365, 'days').startOf('week');

	while (date.isBefore(curDate)) {
		dates.push({
			m: date.clone(),
			dt: date.format('LLLL'),
		});
		date.add(1, 'day');
	}
	return dates;
}

function fillTable(dates: IHitDate[], container: Element) {
	dates.forEach(({ m, dt }, index) => {
		const item = document.createElement('div');
		item.className = 'heat-item';
		item.classList.add(`heat-item-${Math.floor(Math.random() * 5)}`);
		item.setAttribute('title', dt);
		if (m.get('date') === 1) item.appendChild(getMonth(m));

		if (index < 7) item.appendChild(getDay(m));

		container.appendChild(item);
	});
}

function getDay(m: moment.Moment) {
	const day = document.createElement('div');
	day.className = 'date-text heat-day';
	day.innerText = m.format('dd');
	return day;
}

function getMonth(m: moment.Moment) {
	const month = document.createElement('div');
	month.className = 'date-text heat-month';
	month.innerText = m.format('MMM YY');
	return month;
}
