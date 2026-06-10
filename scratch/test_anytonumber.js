const { toNumber } = require('lodash');

console.log("Number('-Infinity'):", Number('-Infinity'));
console.log("parseFloat('-Infinity'):", parseFloat('-Infinity'));
console.log("toNumber('-Infinity'):", toNumber('-Infinity'));
console.log("typeof toNumber('-Infinity'):", typeof toNumber('-Infinity'));
console.log("isNaN(toNumber('-Infinity')):", isNaN(toNumber('-Infinity')));
