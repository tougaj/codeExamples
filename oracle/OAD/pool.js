import pkg from 'oracledb';
const { OUT_FORMAT_OBJECT, createPool } = pkg;

const pool = await createPool({
	user: process.env.USER_NAME,
	password: process.env.USER_PASSWORD,
	connectString: process.env.CONNECTION_STRING,
	configDir: process.env.WALLET_LOCATION,
	walletLocation: process.env.WALLET_LOCATION,
	walletPassword: process.env.WALLET_PASSWORD,
	poolMin: 1,
	poolMax: 10,
	poolIncrement: 1,
});
console.log('👷 Connection pool created.');

pkg.outFormat = OUT_FORMAT_OBJECT;

async function run() {
	const connection = await pool.getConnection();
	try {
		const result = await connection.execute(
			`select * from v_person p where p.person_id < :id`,
			[10] // bind value for :id
		);

		console.log(result.rows);
	} finally {
		await connection.close();
	}
}

await run();
await pool.close(10); // 10 секунд таймаут
console.log('👷 Connection pool closed.');

process.on('SIGINT', async () => {
	try {
		await pool.close(10); // 10 секунд таймаут
		console.log('👷 Connection pool closed.');
		process.exit(0);
	} catch (err) {
		console.error('Error closing pool:', err);
		process.exit(1);
	}
});

// Виклик:
// USER_NAME=user USER_PASSWORD="pwd" WALLET_PASSWORD="wallet_pwd" CONNECTION_STRING="conn" WALLET_LOCATION="path" node pool.js
