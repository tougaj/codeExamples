"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const dotenv = __importStar(require("dotenv"));
const utils_1 = require("./utils");
dotenv.config();
const PARTS_COUNT = (0, utils_1.getNumberEnvironmentVariable)('PARTS_COUNT', "part's count");
const MAX_FILE_SIZE = (0, utils_1.getNumberEnvironmentVariable)('MAX_FILE_SIZE', 'maximum file size');
const data = (0, utils_1.getData)(MAX_FILE_SIZE);
const totalSize = data.reduce((prev, cur) => prev + cur);
console.log(`Total size is ${totalSize} Mb`);
const partSize = totalSize / PARTS_COUNT;
console.log(`Part size is ${partSize} Mb`);
const groupedData = (0, utils_1.getGroupedData)(data);
// console.log(groupedData);
const measures = (0, utils_1.getMeasures)(PARTS_COUNT, partSize, groupedData);
console.log('Measures', measures);
//# sourceMappingURL=index.js.map