import asyncio
import json
import os
from aiohttp import web
from pyModbusTCP.client import ModbusClient
from iec104 import IEC104Server  # Псевдокод, потрібно реалізувати IEC 104 сервер
import threading

# Завантаження конфігурації
def load_config():
    config_path = os.getenv("CONFIG_PATH", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

config = load_config()

# Підключення до Modbus
modbus_client = ModbusClient(host=config["modbus_ip"], port=config["modbus_port"], auto_open=True)

# Читання даних із датчиків
def read_modbus_data():
    data = {}
    for sensor in config["sensors"]:
        value = modbus_client.read_holding_registers(sensor["register"], 1)
        if value:
            data[sensor["name"]] = value[0] * sensor["scale"]
    return data

# Обробка запиту від GUI
async def handle_gui_request(request):
    return web.json_response(read_modbus_data())

# Запуск веб-сервера
def start_web_server():
    app = web.Application()
    app.add_routes([web.get("/data", handle_gui_request)])
    web.run_app(app, port=8080)

# Запуск IEC 104 сервера (потрібно реалізувати окремо)
def start_iec_server():
    iec_server = IEC104Server()
    iec_server.start()

# Запуск всіх сервісів у потоках
if __name__ == "__main__":
    threading.Thread(target=start_web_server, daemon=True).start()
    threading.Thread(target=start_iec_server, daemon=True).start()
    while True:
        asyncio.sleep(1)
