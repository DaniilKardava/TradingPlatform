// speed
var list = [];
for (var a  = 0; a < 10000001; a++){
    list.push(a);
}
console.log(list);
var datenow = new Date();
console.log(datenow)
var max = -Infinity;
for (var i = 0; i < list.length; i++) {
  if (list[i] > max) {
    max = list[i];
  }
}
console.log(max);
var dateafter = new Date();
console.log(dateafter)