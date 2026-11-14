import app from './index.mjs';
app.use((await import('express')).default.static('dist'));
app.listen(3018,'127.0.0.1',()=>console.log('API http://127.0.0.1:3018'));
