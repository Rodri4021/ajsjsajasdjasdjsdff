import asyncio
import random
import json
from telethon import TelegramClient

class TelegramForwarder:
    def __init__(self, api_id, api_hash, telefono):
        self.api_id = api_id
        self.api_hash = api_hash
        self.telefono = telefono
        self.cliente = TelegramClient('sesion' + telefono, api_id, api_hash)

    async def autorizar(self):
        await self.cliente.start(self.telefono)

    async def obtener_ids_mensajes_aleatorios(self):
        try:
            with open("mensajes.txt", "r") as archivo:
                ids_mensajes = [int(linea.strip()) for linea in archivo.readlines() if linea.strip().isdigit()]
                return ids_mensajes
        except FileNotFoundError:
            print("Archivo de mensajes no encontrado.")
            return []

    async def reenviar_mensaje(self, id_chat_origen, id_mensaje, grupo):
        await self.autorizar()

        try:
            mensaje = await self.cliente.get_messages(id_chat_origen, ids=id_mensaje)
            print(f"Mensaje recuperado: {mensaje.id}")

            await asyncio.sleep(2,5)  # Acá ponen el intervalo de tiempo entre mensajes. Está en función random, por lo que puede ser en cualquier momento entre 2 a 5 segundos. Pueden modificarlo a gusto, pero ese es el valor por defecto para evitar que te baneen.

            try:
                await self.cliente.forward_messages(grupo, mensaje)
                print(f"Cronómetro")
            except Exception as e:
                print(f"Error al cronometrar: {e}")

        except Exception as e:
            print(f"Error al obtener el mensaje: {e}")

    async def reenviar_mensajes_a_grupos(self, id_chat_origen, grupos):
        await self.autorizar()

        ids_mensajes = await self.obtener_ids_mensajes_aleatorios()

        if not ids_mensajes:
            print("No hay IDs de mensajes válidos en mensajes.txt. Abortando.")
            return

        while True:
            try:
                
                random.shuffle(ids_mensajes)

                for i, id_grupo in enumerate(grupos):
                    id_mensaje = ids_mensajes[i % len(ids_mensajes)]

                    try:
                        await self.reenviar_mensaje(id_chat_origen, id_mensaje, id_grupo)
                    except Exception as e:
                        print(f"Saltando el grupo {id_grupo} debido a un error: {e}")
                        continue

                    print(f"Mensaje {id_mensaje} enviado al grupo {id_grupo}")

                print("Todos los mensajes han sido enviados a los grupos. Reiniciando desde el principio.")

            except Exception as e:
                print(f"Error al enviar los mensajes: {e}")

            await asyncio.sleep(5)  # Retardo antes de comenzar el bucle nuevamente. Este es un valor por defecto, pueden modificarlo a gusto.

def leer_configuracion():
    try:
        with open("config.json", "r") as archivo:
            configuracion = json.load(archivo)
            api_id = configuracion.get("api_id")
            api_hash = configuracion.get("api_hash")
            telefono = configuracion.get("telefono")
            return api_id, api_hash, telefono
    except FileNotFoundError:
        print("Archivo de configuración no encontrado.")
        return None, None, None

def leer_grupos():
    try:
        with open("grupos.txt", "r") as archivo:
            grupos = [int(linea.strip()) for linea in archivo.readlines() if linea.strip().isdigit() or (linea.strip().startswith('-') and linea.strip()[1:].isdigit())]
            return grupos
    except FileNotFoundError:
        print("Archivo de grupos no encontrado.")
        return []

async def principal():
    api_id, api_hash, telefono = leer_configuracion()
    grupos = leer_grupos()

    if api_id is None or api_hash is None or telefono is None:
        print("Configuración faltante o incompleta. Verifique config.json.")
        return

    if not grupos:
        print("No se encontraron grupos en grupos.txt.")
        return

    forwarder = TelegramForwarder(api_id, api_hash, telefono)

    id_chat_origen = -10099999999 # Acá tienen que poner la ID del chat del que se extraerán los mensajes a reenviar. Puede ser su canal de refes.
    
    try:
        await forwarder.reenviar_mensajes_a_grupos(id_chat_origen, grupos)
    
    except Exception as e:
        print(f"Error al ejecutar TelegramForwarder: {e}")
    
    finally:
        await forwarder.cliente.disconnect()

if __name__ == "__main__":
    asyncio.run(principal())