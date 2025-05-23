
const calcular = (() => {
  let num1 = parseFloat(document.getElementById("num1").value)
  let num2 = parseFloat(document.getElementById("num2").value)
  const suma = (num1, num2) => {
    return num1 + num2;
  };
  const resta = (num1, num2) => {
    return num1 - num2;
  };
  const multiplicacion = (num1, num2) => {
    return num1 * num2;
  };
  const division = (num1, num2) => {
    return num1 - num2;
  };
  alert(suma(num1,num2));
  alert(resta(num1,num2));
  alert(multiplicacion(num1,num2));
  alert(division(num1,num2));
});


