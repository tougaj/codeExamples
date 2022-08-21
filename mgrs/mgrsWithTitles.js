import { stringify } from 'csv-stringify/sync';

const mgrs_raw = 
`
36T WQ 45623 92649	Тест-С1	20.08.22 07:01:29
37T BL 93603 11555	Тест-С2	19.08.22 14:01:36
37U DP 47939 69614	Тест-С2	19.08.22 21:03:20
`;

const TITLES = ['Координати', 'Назва', 'Дата і час'];

const mgrs_array = mgrs_raw.split('\n').filter(Boolean).map(item => {
	const data = item.trim().split('\t');
	if (data.length !== TITLES.length) {
		console.log(`Невірна кількість стовбців в даних "${item}"\nОчікувалось: ${TITLES.length}, в наявності: ${data.length}`);
		process.exit(1);
	}
	return data;
})

async function main(){
	const {default: Mgrs} = await import('geodesy/mgrs.js');

	const convert = mgrs_string => {
		const mgrs = Mgrs.parse(mgrs_string);
		const latlon = mgrs.toUtm().toLatLon();
		return [latlon._lat, latlon._lon]
		
	}

	const result = [[...TITLES]].concat(mgrs_array.map(item => item.map((s, index) => {
		let res = s;
		if (index === 0) {
			const latlon = convert(s);
			res = latlon.join(' ');
		}
		return res;
	})));

	const output = stringify(result);
	console.log(output);
}

main()