import pkg from 'oracledb';
const { OUT_FORMAT_OBJECT, createPool } = pkg;

pkg.outFormat = OUT_FORMAT_OBJECT;

let pool;

async function initPool() {
	if (!pool) {
		pool = await createPool({
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
	}
	return pool;
}

async function closePool() {
	if (pool)
		try {
			await pool.close(10); // 10 секунд таймаут
			console.log('👷 Connection pool closed.');
			process.exit(0);
		} catch (err) {
			console.error('❌ Error closing pool:', err);
			process.exit(1);
		}
}

async function getConnection() {
	const pool = await initPool();
	return await pool.getConnection();
}

async function withConnection(callback) {
	const connection = await getConnection();

	try {
		const result = await callback(connection);
		await connection.commit();
		console.log('✅ Transaction commit');
		return result;
	} catch (err) {
		await connection.rollback();
		console.log('❌ Transaction rollback');
		throw err;
	} finally {
		await connection.close(); // повернення в пул
	}
}

async function selectWithConnection() {
	await withConnection(async (connection) => {
		const result = await connection.execute(
			`select * from v_person p where p.person_id < :id`,
			[10] // bind value for :id
		);
		console.log(result.rows);
		return result;
	});
}

async function select() {
	const connection = await getConnection();
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

async function update() {
	const connection = await getConnection();
	try {
		const result = await connection.execute(
			'update d_person set PERSON_CODE=:code where person_id=:id',
			{ code: 'A12', id: 2 }
			// ['C11', 2] // bind value for :id
		);
		console.log(result);
		// await connection.commit();
		await connection.rollback();
	} finally {
		await connection.close();
	}
}

await select();
await update();
await selectWithConnection();
closePool();

process.on('SIGINT', async () => {
	closePool();
});

// Виклик:
// USER_NAME=user USER_PASSWORD="pwd" WALLET_PASSWORD="wallet_pwd" CONNECTION_STRING="conn" WALLET_LOCATION="path" node pool.js
