const fs = require('fs');
import * as cheerio from 'cheerio';
const PAGE_TEMPLATE = 'https://nemez1da.ru/voennye-prestupniki/sotrudniki-sbu/sbu/page/';
const LINK_SELECTOR = '.simple-grid-grid-post a';
const PAGE_COUNT = 101;

const wait = (ms: number) => new Promise((response) => setTimeout(response, ms));

const getPage = async (url: string) => {
	await wait(100);
	console.log(`📄 Processing Page ${url}`);
	let pageText: string | undefined;
	try {
		const response = await fetch(url);
		pageText = await response.text();
	} catch (error) {
		console.error(`❌ Error loading page "${url}"`);
	}
	return pageText;
};

const process = async (pages: boolean[], links: Set<string>): Promise<[boolean[], Set<string>]> => {
	for (let index = 0; index < pages.length; index++) {
		if (pages[index]) continue;
		const PageNo = index + 1;
		const url = `${PAGE_TEMPLATE}${PageNo}/`;
		const pageText = await getPage(url);
		if (!pageText) continue;
		const $ = cheerio.load(pageText);
		let linksFound = 0;
		$(LINK_SELECTOR).each(function () {
			const link = $(this).attr('href');
			if (!link) return;
			links.add(link);
			linksFound += 1;
		});
		pages[index] = linksFound !== 0;
		if (linksFound === 0) console.error(`❌ ${linksFound} links found`);
	}
	return [pages, links];
};

(async function main() {
	let pages = new Array(PAGE_COUNT).fill(false);
	let links: Set<string> = new Set();
	let iteration = 0;
	while (pages.some((processed) => !processed)) {
		console.log(`⏬ Iteration ${++iteration}`);
		if (iteration !== 1) await wait(5000);
		const [p, l] = await process(pages, links);
		pages = p;
		links = l;
	}

	const arLinks = [...links];
	arLinks.sort();
	fs.writeFileSync('links.txt', arLinks.join('\n'));
	console.log(`✅ ${arLinks.length} links detected`);
})();
