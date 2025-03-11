import asyncio
import sqlite3
from fastapi import FastAPI
from pymodbus.client.sync import ModbusTcpClient
from iec104 import IEC104Server

app = FastAPI()

db_path = "config.db"

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sensors (
                        id INTEGER PRIMARY KEY,
                        ip TEXT,
                        port INTEGER,
                        register INTEGER,
                        scale REAL
                    )''')
    conn.commit()
    conn.close()

init_db()

def get_sensors():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT ip, port, register, scale FROM sensors")
    sensors = cursor.fetchall()
    conn.close()
    return sensors

def read_modbus_data():
    data = {}
    for ip, port, register, scale in get_sensors():
        client = ModbusTcpClient(ip, port)
        client.connect()
        rr = client.read_holding_registers(register, 1)
        if rr.isError():
            continue
        value = rr.registers[0] * scale
        data[f"{ip}:{register}"] = value
        client.close()
    return data

iec104_server = IEC104Server()

@app.get("/send_iec104")
def send_iec104_data():
    data = read_modbus_data()
    for key, value in data.items():
        iec104_server.send_data(value)
    return {"status": "data sent"}

@app.get("/config")
def get_config():
    return {"sensors": get_sensors()}

@app.post("/config")
def add_sensor(ip: str, port: int, register: int, scale: float):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sensors (ip, port, register, scale) VALUES (?, ?, ?, ?)", (ip, port, register, scale))
    conn.commit()
    conn.close()
    return {"status": "added"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
