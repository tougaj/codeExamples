fetch('https://www.president.gov.ua/rss/news/all.rss')
	.then(response => response.text())
	.then(data => console.log(data))
	.catch(console.error);