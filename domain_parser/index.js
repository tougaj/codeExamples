import psl from 'psl';
// node.js: https://www.npmjs.com/package/psl
// python: https://pypi.org/project/tldextract/

const checkDomainViaPsl = (input) => {
	let domainName;

	try {
		// Якщо це повне посилання, виділяємо hostname
		const url = new URL(input);
		domainName = url.hostname;
	} catch (error) {
		// Якщо це не URL, сприймаємо як домен
		domainName = input;
	}

	console.log(`Checking domain via psl: ${domainName}`);
	console.log('Parsed data:');
	console.log(psl.parse(domainName));
	console.log(`Domain is: ${psl.get(domainName)}`);
};

// Перевірка
const input = 'https://82.mchs.gov.ru/deyatelnost/press-centr/intervyu/3859267?ysclid=m4u0o9bpja768436598';
// const input = '82.mchs.gov.ru';
// const input = 'kherson-news.ru';
// const input = 'my.mail.ru';
// const input = 'https://politics.unian.net/some/page?query=123';
// const input = 'архиерей.рф';
// const input = 'https://архиерей.рф/all/';
checkDomainViaPsl(input);
