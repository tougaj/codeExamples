import { faker, fakerUK, fakerDE, fakerRU } from '@faker-js/faker';

const BASE_COUNT = 2;

const generate = (fn, count = BASE_COUNT) => {
	for (var i = 0; i < count; i++) {
		console.log(fn())
	}	
	console.log('----------')
}

const company = f => () => f.company.name()+' '+f.company.catchPhrase();

generate(fakerUK.person.fullName, BASE_COUNT*2);
generate(fakerRU.person.fullName);
generate(faker.person.fullName);
generate(fakerDE.person.fullName);

generate(fakerUK.company.name, BASE_COUNT*2);
generate(fakerRU.company.name);
generate(company(faker));
generate(fakerDE.company.name);

