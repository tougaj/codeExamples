"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
const parseKMZ = require('parse2-kmz');
const fs = require('fs');
const INPUT_PATH = './input/';
const OUTPUT_PATH = './output/';
const convertKmzToJson = (baseFilename) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const kmz = yield parseKMZ.toJson(`${INPUT_PATH}${baseFilename}.kmz`);
        const json = JSON.stringify(kmz, undefined, 2);
        fs.writeFileSync(`${OUTPUT_PATH}${baseFilename}.json`, json);
        console.log('Done');
    }
    catch (error) {
        console.error(error);
    }
});
convertKmzToJson('Обстановка');
