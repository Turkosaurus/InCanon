// Generates random number to simulate dice roll
function random(min, max)
{
return Math.floor(Math.random() * (max - min) ) + min + 1;
}

function roll()
{
// let qty = document.querySelector('#qty').value
let die = document.querySelector('#die').value
// let mod = document.querySelector('#mod').value

let total = 0
let result = random(0, die)

alert("you've rolled a " + result);
// document.querySelector('#display').innerHTML = 'result - '+ result;
}