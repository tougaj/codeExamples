"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const moment_1 = __importDefault(require("moment"));
moment_1.default.locale('uk-UA');
document.addEventListener('DOMContentLoaded', () => {
    const dates = fillDates();
    const container = document.querySelector('.container');
    if (!container)
        return;
    fillTable(dates, container);
});
function fillDates() {
    const curDate = moment_1.default();
    const dates = [];
    const date = moment_1.default().subtract(365, 'days').startOf('week');
    while (date.isBefore(curDate)) {
        dates.push({
            m: date.clone(),
            dt: date.format('dd, LL'),
        });
        date.add(1, 'day');
    }
    return dates;
}
function fillTable(dates, container) {
    dates.forEach(({ m, dt }, index) => {
        const item = document.createElement('div');
        item.className = 'heat-item';
        item.classList.add(`heat-item-${Math.floor(Math.random() * 5)}`);
        item.setAttribute('title', dt);
        if (m.get('date') === 1) {
            item.classList.add('first-day');
            item.appendChild(getMonth(m));
        }
        if (index < 7)
            item.appendChild(getDay(m));
        container.appendChild(item);
    });
}
function getDay(m) {
    const day = document.createElement('div');
    day.className = 'date-text heat-day';
    day.innerText = m.format('dd');
    return day;
}
function getMonth(m) {
    const month = document.createElement('div');
    month.className = 'date-text heat-month';
    month.innerText = m.format('MMM YY');
    return month;
}
