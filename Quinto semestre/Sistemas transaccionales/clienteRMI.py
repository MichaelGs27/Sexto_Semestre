import Pyro5.api

#solicito al usuaario que introduzca el URI del servidor
uri = input("Introduce el URI del servicio TiposID:  ")

#Crea un proxy que permite al cliente llamar metodos remotos como si fueran locales
tipos_id_remoto = Pyro5.api.Proxy(uri)

try:
    #solicita al usuario que ingrese el codigo que desea consultar
    codigo = input("Ingrese el codigo deltipo de identificacion (ej: CC,TI,CE,PA):  ")

    #llama remotamente al metodo consultar_descripcion pasanado el codigo
    descripcion = tipos_id_remoto.consultar_descripcion(codigo.upper())

    #Muestra la despcripcionn recibida desde el servidor
    print(f"Descripcion:{descripcion}")
except Exception as e:
    #Captura y muestra cualquier error ocurrido durante la comunicacion o ejecucion remota
    print(f"Error consultando el servicio remoto: {e}")
