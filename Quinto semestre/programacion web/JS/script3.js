"use strict";

var contenedor = document.getElementById("resultados");

var textDiv = "";

// consume el servicio de pokeapi con Fetch

window.addEventListener("load", function () {
  fetch("https://pokeapi.co/api/v2/pokemon?limit=50&offset=0")
    .then((data) => data.json())

    .then((data) => {
      console.info(data.results);

      // recorre el objeto consumido

      data.results.map((pokemon, i) => {
        // cada vez que se itera se agrega al DOM

        addPokemon(pokemon.url);
      });
    });
});

function addPokemon(url) {
  fetch(url)
    .then((data) => data.json())
    .then((data) => {
      console.info(data);
      mostrarPokemon(data);
    });
}
function mostrarPokemon(pokemon) {
  textDiv += '<div class="col-md-4"><div class="card" >';
  textDiv +='<img class="card-img-top" src="' +pokemon.sprites.other.home.front_default +'" alt="Card image">';
  textDiv +='<div class="card-body"><h4 class="card-title">' +pokemon.name +'</h4><p class="card-text">';
  textDiv +='Some example text.</p><a href="perfil.php?id=" + pokemon.id +" class="btn btn-primary">';
  textDiv += "Ver pokemon</a></div></div></div>";
  console.info(pokemon)
  contenedor.innerHTML = textDiv;
}
