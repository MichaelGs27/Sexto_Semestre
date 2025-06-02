btnEnviar = document.getElementById("btnEnviar");
let carrito = [];

const columnaBody = document.getElementById("columna");

btnEnviar.addEventListener("click", () => {
  capturarProducto();
  LimpiarForm();
  mostrarProductos();
  alert("Producto agregado correctamente");
});

columnaBody.addEventListener("click", (event) => {
    // Comprobar si el clic fue en un botón con la clase 'eliminar'
    if (event.target.classList.contains("eliminar")) {
        const productoAEliminar = event.target.dataset.producto;
        eliminarProducto(productoAEliminar);
    }
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
        imprimir += `
            <tr>
              <td>${productos.producto}</td>
              <td>${productos.precio}</td>
              <td>${productos.cantidad}</td>
              <td>
                  <button class="eliminar btn btn-danger btn-sm" data-producto="${productos.producto}">Eliminar</button>
              </td>
            </tr>`;
    });
    document.getElementById("columna").innerHTML = imprimir;
};

const eliminarProducto = (nombreProducto) => {
    carrito = carrito.filter((producto) => producto.producto !== nombreProducto);
    console.log("Carrito después de eliminar:", carrito);
    mostrarProductos(); // Volver a renderizar la tabla
};
//  Como se define una funcion
//  const nuevafuncion =(()=>{

// })
