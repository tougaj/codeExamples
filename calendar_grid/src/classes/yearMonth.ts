/**
 * В даному класі у всіх інтерфейсних методах використовується людський місяць,
 * тобто його значення є від 1 до 12.
 * (На відміну від місяців JavaScript, які в об'єкті Date мають значення від 0 до 11)
 */
export class YearMonth {
	#date: Date;

	constructor(strDate?: string) {
		this.#date = new Date(...this.#splitStrDate(strDate));
	}

	#splitStrDate(strDate?: string): [number, number] {
		let [year, month] = (strDate || '').split('-').map(Number);
		if (!year || !month) {
			const now = new Date();
			year = now.getFullYear();
			month = now.getMonth() + 1;
		}
		return [year, month - 1];
	}

	get value(): Date {
		return this.#date;
	}

	set date(newDate: string) {
		this.#date = new Date(...this.#splitStrDate(newDate));
	}

	getYM(): [number, number] {
		return [this.#date.getFullYear(), this.#date.getMonth() + 1];
	}

	toISOString() {
		return this.#date.toISOString();
	}

	#addMonth(delta: number) {
		this.#date.setMonth(this.#date.getMonth() + delta);
		return this;
	}

	inc(delta = 1) {
		return this.#addMonth(delta);
	}

	dec(delta = 1) {
		return this.#addMonth(-delta);
	}

	firstDoW() {
		return this.#date.getDay();
	}

	daysCount() {
		return new Date(...this.getYM(), 0).getDate();
	}
}
