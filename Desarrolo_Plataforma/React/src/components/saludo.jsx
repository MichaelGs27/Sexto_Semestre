import Apellido from './apellido'
function Saludo({ nombre, ape }) {
  return <>
        <h1>¡Hola, {nombre}! </h1> ;
        <h2>Tu apellido es: <Apellido nombre={ape} /></h2>
  </>
}
export default Saludo;