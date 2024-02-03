const fs = require('fs');
require('log-timestamp');
var watch = require('node-watch');

const filePath = './test.txt';

const watcher = watch(filePath, { recursive: false, delay: 1000 });
watcher.on('change', function(evt, name) {
	console.log('✅ %s changed.', name);
});
watcher.on('error', (err)=>{
	console.log('❗', err);
})
// watch(filePath, { recursive: false }, function(evt, name) {
// 	console.log('%s changed.', name);
// });

// Тут множинне спрацювання. І якщо використовувати цей метод, то треба робити debounce.
// const fs = require('fs');
// fs.watch(filePath, (event, filename) => {
//   if (filename) {
//     console.log(`${filename} file Changed`);
//   }
// });


