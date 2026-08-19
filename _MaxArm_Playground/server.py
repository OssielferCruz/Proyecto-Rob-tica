import os
import sys
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from maxarm_controller import MaxArmController

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

arm: MaxArmController = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global arm
    print("[SERVER] Inicializando controlador MaxArm en COM6...")
    arm = MaxArmController(port="COM6", baudrate=115200)
    yield
    print("[SERVER] Cerrando puerto serial COM6...")
    if arm:
        arm.close()

app = FastAPI(title="MaxArm Interactive Dashboard Server", lifespan=lifespan)

dashboard_dir = os.path.join(os.path.dirname(__file__), "dashboard")
if not os.path.exists(dashboard_dir):
    os.makedirs(dashboard_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=dashboard_dir), name="static")

@app.get("/")
async def get_index():
    index_path = os.path.join(dashboard_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Dashboard de MaxArm inicializándose...</h1>")

GAMES_CATALOG = [
    {
        "id": "color_sorting",
        "category": "Sensor de Color APDS-9960",
        "name": "Clasificación por Color",
        "description": "Identifica bloques de colores y los transporta a sus receptáculos.",
        "icon": "🎨",
        "rel_path": "Appendix/7. Sensor-extension Game Program Files/Python Development/Program Files/8. Color Sorting/main.py",
        "bundle_files": [
            {"source": "../../Driver Libraries/Color_sensor.py", "remote": "Color_sensor.py"},
            {"source": "../../Driver Libraries/Color_CONST.py", "remote": "Color_CONST.py"},
            {"source": "main.py", "remote": "main.py"}
        ]
    },
    {
        "id": "waste_sorting",
        "category": "WonderCam AI Vision",
        "name": "Clasificación de Residuos (IA)",
        "description": "Reconoce tarjetas de residuos con la cámara WonderCam y los clasifica (2 a la izquierda, 2 a la derecha).",
        "icon": "♻️",
        "rel_path": "Appendix/12. AI Vision Game Program Files/Python Development/Program Files/Waste Sorting/main.py",
        "bundle_files": [
            {"source": "../Driver Libraries/PID.py", "remote": "PID.py"},
            {"source": "../Driver Libraries/WonderCam.py", "remote": "WonderCam.py"},
            {"source": "../Driver Libraries/FanModule.py", "remote": "FanModule.py"},
            {"source": "../Driver Libraries/Stepper.py", "remote": "Stepper.py"},
            {"source": "../Driver Libraries/TM1640.py", "remote": "TM1640.py"},
            {"source": "main.py", "remote": "main.py"}
        ]
    },
    {
        "id": "color_tracking_sorting",
        "category": "WonderCam AI Vision",
        "name": "Seguimiento y Ordenamiento por Color",
        "description": "Reconoce colores con WonderCam, los sigue con PID y los ordena al detenerse.",
        "icon": "🎯",
        "rel_path": "Appendix/12. AI Vision Game Program Files/Python Development/Program Files/Color Tracking and Sorting/main.py",
        "bundle_files": [
            {"source": "../Driver Libraries/PID.py", "remote": "PID.py"},
            {"source": "../Driver Libraries/WonderCam.py", "remote": "WonderCam.py"},
            {"source": "../Driver Libraries/FanModule.py", "remote": "FanModule.py"},
            {"source": "../Driver Libraries/Stepper.py", "remote": "Stepper.py"},
            {"source": "../Driver Libraries/TM1640.py", "remote": "TM1640.py"},
            {"source": "main.py", "remote": "main.py"}
        ]
    },
    {
        "id": "handle_control",
        "category": "Control Inalámbrico USB / Gamepad",
        "name": "Control por Mando Inalámbrico / Consola",
        "description": "Permite mover los ejes cartesiano XYZ, succión y rotación con el mando inalámbrico USB.",
        "icon": "🎮",
        "rel_path": "Appendix/9. Handle Control Programs/main.py",
        "bundle_files": [
            {"source": "USBDevice.py", "remote": "USBDevice.py"},
            {"source": "RobotControl.py", "remote": "RobotControl.py"},
            {"source": "SuctionNozzle.py", "remote": "SuctionNozzle.py"},
            {"source": "main.py", "remote": "main.py"}
        ]
    },
    {
        "id": "multi_remote_control",
        "category": "Control Múltiple (Mando, App & PC)",
        "name": "Control Múltiple (Mando PS2, App & PC)",
        "description": "Programa maestro para controlar el MaxArm simultáneamente por Mando USB, App Móvil (BLE) y PC.",
        "icon": "📱",
        "rel_path": "Appendix/10. Multiple Remote Control and PC Software Program/main.py",
        "bundle_files": [
            {"source": "../9. Handle Control Programs/USBDevice.py", "remote": "USBDevice.py"},
            {"source": "../9. Handle Control Programs/RobotControl.py", "remote": "RobotControl.py"},
            {"source": "../9. Handle Control Programs/SuctionNozzle.py", "remote": "SuctionNozzle.py"},
            {"source": "main.py", "remote": "main.py"}
        ]
    }
]

@app.get("/api/games")
async def list_games():
    return GAMES_CATALOG

@app.post("/api/run_game/{game_id}")
async def run_game(game_id: str):
    target_game = next((g for g in GAMES_CATALOG if g["id"] == game_id), None)
    if not target_game:
        return JSONResponse({"status": "error", "message": "Juego no encontrado"}, status_code=404)

    script_path = os.path.join(REPO_ROOT, target_game["rel_path"])
    if not os.path.exists(script_path):
        return JSONResponse({"status": "error", "message": f"Archivo de código no encontrado: {script_path}"}, status_code=404)

    try:
        if not arm or not arm.is_connected:
            return JSONResponse({"status": "error", "message": "El controlador MaxArm no está conectado"}, status_code=503)

        with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
            code_content = f.read()

        # Reemplazar el entry point para poder ejecutar el script desde RAW REPL.
        code_clean = code_content.replace("if __name__ == '__main__':", "if True:")

        # Calibración de Trigger Visual Directo y Estabilización:
        if game_id == "color_tracking_sorting":
            # 1. Ganancia PID adecuada para centrado fluido
            code_clean = code_clean.replace("PID(0.08, 0.003, 0.0003)", "PID(0.04, 0.0015, 0.00015)")
            
            # 2. Velocidad de servos (100ms por paso) y retardo de cámara (80ms)
            code_clean = code_clean.replace("arm.set_position((x,y,z),50)", "arm.set_position((x,y,z),100)")
            code_clean = code_clean.replace("time.sleep_ms(50)", "time.sleep_ms(80)")

            # 3. Trigger visual directo (28x22px) y confirmacion fluida de 4 lecturas (~0.5s)
            code_clean = code_clean.replace("if abs(dx) < 0.1 and abs(dy) < 0.1:", "if abs(center_x - 160) < 28 and abs(center_y - 120) < 22:")
            code_clean = code_clean.replace("if i > 10:", "if i > 4:")
            
            # 4. Ajuste fino de caída al centro exacto del cubo (d_y = 80mm, +18mm a la derecha, Z=76mm)
            code_clean = code_clean.replace("d_x = x/2.3", "d_x = (x / 2.3) + 18")
            code_clean = code_clean.replace("d_y = (68-abs(d_x/3))", "d_y = 80")
            code_clean = code_clean.replace("arm.set_position((x+d_x,y-d_y,86),600)", "arm.set_position((x+d_x,y-d_y,76),750)")
        elif game_id == "waste_sorting":
            # 1. Ajustar la cota de bajada Z para tomar tarjetas del suelo (reducir Z a 40mm):
            code_clean = code_clean.replace("arm.set_position((x,y-d_y,50),600)", "arm.set_position((x,y-d_y,40),600)")
            
            # 2. Redistribuir contenedores: 2 a la izquierda (-120mm) y 2 a la derecha (+120mm)
            # Peligrosos (Izq Fondo): (-120, -140, 60)
            code_clean = code_clean.replace("(place_x, place_y, place_z) = (-120,-170,60)", "(place_x, place_y, place_z) = (-120,-140,60)")
            # Reciclables (Izq Frente): (-120, -60, 60)
            code_clean = code_clean.replace("(place_x, place_y, place_z) = (-120,-120,60)", "(place_x, place_y, place_z) = (-120,-60,60)")
            # Orgánicos (Der Frente): (120, -60, 60)
            code_clean = code_clean.replace("(place_x, place_y, place_z) = (-120,-70,60)", "(place_x, place_y, place_z) = (120,-60,60)")
            # Otros (Der Fondo): (120, -140, 60)
            code_clean = code_clean.replace("(place_x, place_y, place_z) = (-120,-20,60)", "(place_x, place_y, place_z) = (120,-140,60)")
        elif game_id in ["handle_control", "multi_remote_control"]:
            # Configurar R1 como Toggle (ON/OFF) y asegurar que R2 apague la boquilla al instante
            r1_patch = "elif msg == PSB_R1 | PSB_PRESS:\n      if nozzle.nozzle_st:\n        nozzle.off()\n      else:\n        nozzle.on()\n      which_button_press = msg"
            code_clean = code_clean.replace("elif msg == PSB_R1 | PSB_PRESS: # 打开气泵\n      nozzle.on()\n      which_button_press = msg", r1_patch)
        else:
            code_clean = code_clean.replace("abs(dx) < 0.1 and abs(dy) < 0.1", "abs(dx) < 0.8 and abs(dy) < 0.8")
            code_clean = code_clean.replace("if i > 10:", "if i > 3:")

        # Inyectar filtro inteligente de blobs sin recursión infinita
        if "cam = WonderCam(i2c)" in code_clean:
            patch_code = """cam = WonderCam(i2c)
_raw_get_blob = cam.get_color_blob
def _filtered_get_color_blob(id_num):
    d = _raw_get_blob(id_num)
    if d and 15 <= d[2] <= 130 and 15 <= d[3] <= 130:
        return d
    return None
cam.get_color_blob = _filtered_get_color_blob"""
            code_clean = code_clean.replace("cam = WonderCam(i2c)", patch_code)

        bundle_files = target_game.get("bundle_files", [os.path.basename(script_path)])
        script_dir = os.path.dirname(script_path)

        # Interrupción previa atómica para limpiar cualquier loop previo en el ESP32.
        arm.ser.write(b'\x02\x03\x03\r\n')
        await asyncio.sleep(0.3)

        def build_write_script(remote_name: str, file_content: str) -> str:
            return f"with open({remote_name!r}, 'w') as f: f.write({repr(file_content)})\nprint({remote_name!r} + '_WRITE_OK')\n"

        for bundle_entry in bundle_files:
            if isinstance(bundle_entry, str):
                local_path = os.path.join(script_dir, bundle_entry)
                remote_name = bundle_entry
            else:
                local_path = os.path.join(script_dir, bundle_entry.get("source", bundle_entry.get("remote", "")))
                remote_name = bundle_entry.get("remote", os.path.basename(local_path))

            if not os.path.exists(local_path):
                return JSONResponse({"status": "error", "message": f"Archivo de dependencia no encontrado: {local_path}"}, status_code=404)

            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                file_content = f.read()

            if remote_name == "main.py":
                file_content = code_clean

            arm.exec_raw_repl(build_write_script(remote_name, file_content))
            await asyncio.sleep(0.35)

        # Ejecutar main.py en RAW REPL.
        arm.exec_raw_repl("exec(open('main.py').read())\n")
        await asyncio.sleep(0.3)

        return JSONResponse({
            "status": "ok",
            "message": f"Juego '{target_game['name']}' cargado.",
            "path": script_path
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    await websocket.send_json({
        "type": "telemetry",
        "is_connected": arm.is_connected if arm else False,
        "port": arm.port if arm else "COM6",
        "xyz": arm.current_xyz if arm else [0, -163, 212],
        "suction": arm.suction_state if arm else False
    })

    try:
        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            action = data.get("action")

            if action == "set_xyz" and arm:
                x = data.get("x", 0)
                y = data.get("y", -163)
                z = data.get("z", 212)
                move_time = data.get("time", 500)
                arm.set_xyz(x, y, z, move_time)
                await manager.broadcast({
                    "type": "telemetry",
                    "is_connected": arm.is_connected,
                    "port": arm.port,
                    "xyz": arm.current_xyz,
                    "suction": arm.suction_state
                })

            elif action == "suction" and arm:
                state = data.get("state", False)
                arm.set_suction_nozzle(state)
                await manager.broadcast({
                    "type": "telemetry",
                    "is_connected": arm.is_connected,
                    "port": arm.port,
                    "xyz": arm.current_xyz,
                    "suction": arm.suction_state
                })

            elif action == "set_servo" and arm:
                angle = data.get("angle", 0)
                arm.set_pwm_servo(angle)

            elif action == "home" and arm:
                arm.go_home()
                await manager.broadcast({
                    "type": "telemetry",
                    "is_connected": arm.is_connected,
                    "port": arm.port,
                    "xyz": arm.current_xyz,
                    "suction": arm.suction_state
                })

            elif action == "stop_game" and arm:
                arm.stop_game()
                await manager.broadcast({
                    "type": "telemetry",
                    "is_connected": arm.is_connected,
                    "port": arm.port,
                    "xyz": arm.current_xyz,
                    "suction": arm.suction_state
                })

            elif action == "reconnect" and arm:
                arm.connect()
                await manager.broadcast({
                    "type": "telemetry",
                    "is_connected": arm.is_connected,
                    "port": arm.port,
                    "xyz": arm.current_xyz,
                    "suction": arm.suction_state
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)