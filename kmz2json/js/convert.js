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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const parseKMZ = require('parse2-kmz');
const fs_1 = __importDefault(require("fs"));
const INPUT_PATH = './input/';
const OUTPUT_PATH = './output/';
const convertKmzToJson = (baseFilename) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const kmz = yield parseKMZ.toJson(`${INPUT_PATH}${baseFilename}`);
        const json = JSON.stringify(kmz, undefined, 2);
        fs_1.default.writeFileSync(`${OUTPUT_PATH}${baseFilename}.json`, json);
        console.log(`${baseFilename} converted`);
        return true;
    }
    catch (error) {
        console.error(`Error converting file ${baseFilename}: ${error}`);
    }
    return false;
});
const convertFiles = () => __awaiter(void 0, void 0, void 0, function* () {
    const files = fs_1.default.readdirSync(INPUT_PATH).filter((file) => file.endsWith('.kmz'));
    yield Promise.all(files.map((file) => convertKmzToJson(file)));
    console.log('All files converted');
});
const init = () => {
    if (!fs_1.default.existsSync(OUTPUT_PATH))
        fs_1.default.mkdirSync(OUTPUT_PATH);
};
init();
convertFiles();
