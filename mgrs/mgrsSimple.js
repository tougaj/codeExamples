const mgrs_raw = 
`
37U CR 10865 71580
37U  CR 12286 70848    
36T VS 55130 82695          
`;
const mgrs_array = mgrs_raw.split('\n').filter(Boolean).map(s => s.trim());

async function main(){
	const {default: Mgrs} = await import('geodesy/mgrs.js');

	const convert = mgrs_string => {
		const mgrs = Mgrs.parse(mgrs_string);
		const latlon = mgrs.toUtm().toLatLon();
		return [latlon._lat, latlon._lon]
		
	}

	for (mgrs_string of mgrs_array){
		const latlon = convert(mgrs_string);
		console.log(`${mgrs_string} - ${latlon.join(', ')}`);
	}

	// const mgrs = Mgrs.parse('31U DQ 48251 11932');
	// const latlon = mgrs.toUtm().toLatLon();
	// console.log(latlon.toString('dms', 2));
	// console.assert(latlon.toString('dms', 2) == '48° 51′ 29.50″ N, 002° 17′ 40.16″ E');

	// const p = Mgrs.LatLon.parse('51°28′40.37″N, 000°00′05.29″W');
	// const ref = p.toUtm().toMgrs();
	// console.assert(ref.toString() == '30U YC 08215 07233');
}

main()