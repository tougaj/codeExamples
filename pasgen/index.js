const PASSWORDS_COUNT = 50;
const PASSWORD_LENGTH = 10;
// console.log(`${generateDictionaryPart(48, 57)}${generateDictionaryPart(65, 90)}${generateDictionaryPart(97, 122)}`);
// const DICTIONARY = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
// Вилучив поки нулі та букви О (вони дуже схожі)
const DICTIONARY = '123456789ABCDEFGHIJKLMNPQRSTUVWXYZabcdefghijklmnpqrstuvwxyz'.split('');
const DICTIONARY_LENGTH = DICTIONARY.length;

// function generateDictionaryPart(firstCode, lastCode) {
// 	let part = '';
// 	for (let index = firstCode; index < lastCode + 1; index++) {
// 		part += String.fromCharCode(index);
// 	}
// 	return part;
// }

const generatePassword = () => {
	let pass = '';
	for (let index = 0; index < PASSWORD_LENGTH; index++) {
		const charIndex = Math.floor(Math.random() * DICTIONARY_LENGTH);
		const char = DICTIONARY[charIndex];
		pass += char;
	}
	return pass;
};

for (let index = 0; index < PASSWORDS_COUNT; index++) {
	const pass = generatePassword();
	console.log(pass);
}
