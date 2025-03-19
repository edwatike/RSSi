const jwt = require('jsonwebtoken');

const JWT_SECRET = 'your-secret-key'; // Тот же ключ, что в articles.js
const USERNAME = 'user'; // Замени на свое имя пользователя
const PASSWORD = 'password'; // Замени на свой пароль

module.exports = (req, res) => {
  const { username, password } = req.body;
  if (username === USERNAME && password === PASSWORD) {
    const token = jwt.sign({ user: username }, JWT_SECRET, { expiresIn: '1h' });
    res.json({ token });
  } else {
    res.status(401).send('Invalid credentials');
  }
};