// extract.js
import { Readability } from '@mozilla/readability';
import { JSDOM } from 'jsdom';

async function extractArticle(url) {
  const response = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ArticleBot/1.0)' },
  });
  const html = await response.text();

  const dom = new JSDOM(html, { url });
  const document = dom.window.document;

  // 📸 og:image треба брати ДО parse(), бо Readability чистить/змінює DOM
  const ogImage = document
    .querySelector('meta[property="og:image"]')
    ?.getAttribute('content') ?? null;

  const reader = new Readability(document);
  const article = reader.parse();

  if (!article) {
    console.warn(`⚠️ Не вдалося виділити статтю: ${url}`);
    return null;
  }

  console.log(article, '-----')
  return {
    title: article.title,
    author: article.byline,
    publishedTime: article.publishedTime,
    siteName: article.siteName,
    excerpt: article.excerpt,
    lang: article.lang,
    image: ogImage,
    text: article.textContent.trim(),
    length: article.length,
  };
}

// приклад використання
const data = await extractArticle('https://bihus.info/ogp-vidkryv-dva-kryminalni-provadzhennya-shhodo-nardepa-medyanyka-pislya-rozsliduvannya-bihus-info/');

if (data) {
  console.log('📰 Заголовок:', data.title);
  console.log('✍️ Автор:', data.author ?? 'невідомо');
  console.log('📅 Дата публікації:', data.publishedTime ?? 'невідомо');
  console.log('🌐 Сайт:', data.siteName ?? 'невідомо');
  console.log('🖼️ Зображення:', data.image ?? 'немає');
  console.log('📏 Довжина тексту:', data.length, 'символів');
  console.log('---');
  console.log(data.text.slice(0, 500) + '…');
}