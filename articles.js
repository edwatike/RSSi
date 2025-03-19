const { parse } = require('rss-to-json');
const DeepL = require('deepl-node');
const fs = require('fs');
const fetch = require('node-fetch');
const jwt = require('jsonwebtoken');

const translator = new DeepL('49a435b1-7380-4a48-bf9d-11b5db85f42b:fx');
const RSS_FEEDS = [
  'https://towardsdatascience.com/feed',
  'https://venturebeat.com/feed/',
  'https://rss.app/feeds/PNcbNOcr3uiLMKOm.xml'
];
const TELEGRAM_TOKEN = '7763394832:AAFzvdwFrxtzfVeaJMwCDvsoD0JmYZ7Tkqo';
const CHAT_ID = '-1002447054616';
const JWT_SECRET = 'your-secret-key'; // Замени на свой секретный ключ

async function sendToTelegram(article, domain) {
  const message = `**${article.title}**\n${article.content}\n[Подробнее...](${domain})`;
  const url = `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`;
  await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: CHAT_ID,
      text: message,
      parse_mode: 'Markdown'
    })
  });
}

module.exports = async (req, res) => {
  // Проверка JWT
  const token = req.headers.authorization?.split(' ')[1];
  try {
    jwt.verify(token, JWT_SECRET);
  } catch {
    return res.status(401).send('Invalid or missing token');
  }

  let articles = [];
  const articlesPath = 'public/articles.json';
  if (fs.existsSync(articlesPath)) {
    articles = JSON.parse(fs.readFileSync(articlesPath));
  }

  for (const feed of RSS_FEEDS) {
    try {
      const rss = await parse(feed);
      for (const item of rss.items) {
        if (!articles.some(a => a.id === item.id)) {
          const titleRu = (await translator.translateText(item.title, null, 'ru')).text;
          const contentRu = (await translator.translateText(item.description || 'Нет описания', null, 'ru')).text;
          const newArticle = {
            id: item.id || item.link,
            title: titleRu,
            content: contentRu,
            date: item.published || new Date().toISOString(),
            link: item.link
          };
          articles.push(newArticle);
          // Отправка в Telegram после добавления статьи
          const domain = req.headers.host || 'https://your-vercel-app.vercel.app';
          await sendToTelegram(newArticle, domain);
        }
      }
    } catch (e) {
      console.error(`Ошибка обработки ${feed}: ${e}`);
    }
  }

  fs.writeFileSync(articlesPath, JSON.stringify(articles));
  res.json(articles);
};