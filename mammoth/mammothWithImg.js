var mammoth = require("mammoth");
const fs = require('fs');
const path = require('path');

let imageCounter = 1;
let imgDir = './img';

const options = {
    convertImage: mammoth.images.inline(function(element) {
        return element.read("base64").then(function(imageBuffer) {
            const imgType = element.contentType.split('/').pop();
            const imgName = `image${imageCounter}.${imgType}`;
            const imgPath = path.join(imgDir, imgName);
            fs.writeFile(imgPath, imageBuffer, 'base64', err => {
                if (err) {
                    console.log(err);
                } else {
                    console.log(`${imgPath} was saved.`);
                }
            });

            imageCounter++;

            return {
                src: imgPath
                // src: `data:image/${imgType};base64,${imageBuffer}`
            };
        });
    }),
};

mammoth.convertToHtml({
    path: 'Doc1.docx'
}, options).then(result => {
    var messages = result.messages; // Any messages, such as warnings during conversion
    fs.writeFileSync('test.html', result.value);
}).done();
