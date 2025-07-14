import pkg from 'oracledb';
const { OUT_FORMAT_OBJECT, getConnection } = pkg;

pkg.outFormat = OUT_FORMAT_OBJECT;

async function run() {
	const connection = await getConnection({
		user: process.env.USER_NAME,
		password: process.env.USER_PASSWORD,
		connectString: process.env.CONNECTION_STRING,
		configDir: process.env.WALLET_LOCATION,
		walletLocation: process.env.WALLET_LOCATION,
		walletPassword: process.env.WALLET_PASSWORD,
	});

	const result = await connection.execute(
		`select * from v_person p where p.person_id < :id`,
		[10] // bind value for :id
	);

	console.log(result.rows);
	await connection.close();
}

run();

// Виклик:
// USER_NAME=user USER_PASSWORD="pwd" WALLET_PASSWORD="wallet_pwd" CONNECTION_STRING="conn" WALLET_LOCATION="path" node test.js
