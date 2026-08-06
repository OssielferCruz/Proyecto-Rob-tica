# Guia de ejecucion de MaxArm

Este repositorio incluye el material completo del proyecto MaxArm y el Playground de control.
Para abrirlo en una PC nueva, sigue estos pasos.

## Requisitos

- Windows 10 o 11.
- Python 3.11 o superior.
- Git.
- Git LFS instalado, porque el repositorio usa archivos grandes.
- El brazo MaxArm conectado por USB y disponible como `COM6`.

## Instalacion rapida

1. Clona el repositorio.
2. Abre una consola en la raiz del proyecto.
3. Ejecuta `instalar_maxarm.bat`.

El script crea `.venv`, instala las librerias y activa Git LFS.

## Arranque manual

Si prefieres hacerlo a mano:

```bat
git lfs install
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cd _MaxArm_Playground
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

## Uso del proyecto

1. Conecta el MaxArm por USB.
2. Verifica que el puerto serial sea `COM6`.
3. Inicia el servidor con el comando anterior.
4. Abre `http://127.0.0.1:8000/` en el navegador.
5. Usa el panel para mover el brazo, activar succión y ejecutar los modos de vision.

## Nota importante sobre los archivos grandes

El repositorio utiliza Git LFS para almacenar instaladores, videos y otros binarios pesados.
Si la primera descarga deja archivos punteados o vacios, ejecuta:

```bat
git lfs pull
```

## Solucion de problemas

- Si el servidor no abre, revisa que el puerto `8000` no este ocupado.
- Si el brazo no conecta, confirma que `COM6` sea el puerto correcto en tu PC.
- Si faltan librerias, vuelve a ejecutar `instalar_maxarm.bat` dentro de una consola abierta como usuario normal.