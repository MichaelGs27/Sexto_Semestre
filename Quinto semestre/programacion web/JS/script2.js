btnEnviar = document.getElementById("btnEnviar");
let carrito = [];

btnEnviar.addEventListener("click", () => {
  capturarProducto();
  LimpiarForm();
  mostrarProductos();
  alert("Producto agregado correctamente");
});

const LimpiarForm = () => {
  document.getElementById("producto").value = "";
  document.getElementById("precio").value = "";
  document.getElementById("cantidad").value = "";
};

const capturarProducto = () => {
  producto = document.getElementById("producto").value;
  precio = document.getElementById("precio").value;
  cantidad = document.getElementById("cantidad").value;
  agregarProducto(producto, precio, cantidad);
};

const agregarProducto = (producto, precio, cantidad) => {
  const productos = {};
  productos.producto = producto;
  productos.precio = precio;
  productos.cantidad = cantidad;
  carrito.push(productos);
  console.info(carrito)
};

const mostrarProductos = () => {
  let imprimir = "";
  carrito.forEach((productos) => {
    imprimir +=
      "<h5>El nombre del producto es: " +
      productos.producto +
      " - precio: " +
      productos.precio +
      " - cantidad: " +
      productos.cantidad +
      " </h5>";
  });
  document.getElementById("mostrar").innerHTML = imprimir;
};

//  Como se define una funcion
//  const nuevafuncion =(()=>{

// })
