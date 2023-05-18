import { YearMonth } from '../yearMonth';

describe('yearMonth', () => {
	const yearMonth = new YearMonth('2023-02-05');

	it('toISOString', () => {
		expect(yearMonth.toISOString()).toBe('2023-01-31T22:00:00.000Z');
		expect(new YearMonth('2023-05-11').toISOString()).toBe('2023-04-30T21:00:00.000Z');
	});

	it('firstDoW', () => {
		expect(yearMonth.firstDoW()).toBe(3);
		expect(new YearMonth('2023-05-11').firstDoW()).toBe(1);
		expect(new YearMonth('2023-01-24').firstDoW()).toBe(0);
	});

	it('daysCountInMonth', () => {
		expect(yearMonth.daysCount()).toBe(28);
		expect(new YearMonth('2023-05-11').daysCount()).toBe(31);
		expect(new YearMonth('2023-04-01').daysCount()).toBe(30);
		expect(new YearMonth('2020-02-17').daysCount()).toBe(29);
	});

	it('getData', () => {
		expect(yearMonth.getYM()).toEqual([2023, 2]);
	});

	it('adding', () => {
		expect(yearMonth.inc(0).getYM()).toEqual([2023, 2]);
		expect(yearMonth.dec(0).getYM()).toEqual([2023, 2]);
		expect(yearMonth.inc().getYM()).toEqual([2023, 3]);
		expect(yearMonth.dec().getYM()).toEqual([2023, 2]);
		expect(yearMonth.dec(5).getYM()).toEqual([2022, 9]);
		expect(yearMonth.inc(11).getYM()).toEqual([2023, 8]);
		expect(yearMonth.inc(-7).getYM()).toEqual([2023, 1]);
		expect(yearMonth.dec(-1).getYM()).toEqual([2023, 2]);
	});

	it('set date', () => {
		const now = new Date();
		yearMonth.date = 'invalid data';
		expect(yearMonth.getYM()).toEqual([now.getFullYear(), now.getMonth() + 1]);
		yearMonth.date = '2022-11-12';
		expect(yearMonth.getYM()).toEqual([2022, 11]);
	});
});

describe('yearMonth with wrong date', () => {
	const now = new Date();
	const yearMonth = new YearMonth('qqq');
	expect(yearMonth.getYM()).toEqual([now.getFullYear(), now.getMonth() + 1]);
});
