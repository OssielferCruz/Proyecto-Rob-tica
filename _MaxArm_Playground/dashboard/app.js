// MaxArm Pro Studio | Official Repository Code Executor & WonderCam Camera Stream
let ws;

// DOM Elements - Metrics Bar
const txtMetricX = document.getElementById('txtMetricX');
const txtMetricY = document.getElementById('txtMetricY');
const txtMetricZ = document.getElementById('txtMetricZ');
const txtMetricNozzle = document.getElementById('txtMetricNozzle');
const statusBadge = document.getElementById('statusBadge');
const statusText = document.getElementById('statusText');
const btnReconnect = document.getElementById('btnReconnect');

// DOM Elements - Critical Limit Banner
const criticalLimitBox = document.getElementById('criticalLimitBox');
const criticalLimitMsg = document.getElementById('criticalLimitMsg');

// DOM Elements - Sliders & Inputs
const sliderX = document.getElementById('sliderX');
const sliderY = document.getElementById('sliderY');
const sliderZ = document.getElementById('sliderZ');
const valX = document.getElementById('valX');
const valY = document.getElementById('valY');
const valZ = document.getElementById('valZ');

// DOM Elements - Home Reset & Presets
const btnHome = document.getElementById('btnHome');

// DOM Elements - Actuators
const btnToggleSuction = document.getElementById('btnToggleSuction');
const pumpStatusTag = document.getElementById('pumpStatusTag');
const suctionBtnText = document.getElementById('suctionBtnText');
const sliderServo = document.getElementById('sliderServo');
const valServo = document.getElementById('valServo');

// DOM Elements - Badges, Canvas, Programmer & Log
const badgeJ1 = document.getElementById('badgeJ1');
const badgeJ2 = document.getElementById('badgeJ2');
const badgeJ3 = document.getElementById('badgeJ3');
const canvas = document.getElementById('armCanvas');
const ctx = canvas.getContext('2d');

const btnAddAction = document.getElementById('btnAddAction');
const btnRunSequence = document.getElementById('btnRunSequence');
const btnClearSequence = document.getElementById('btnClearSequence');
const actionsTbody = document.getElementById('actionsTbody');
const logConsole = document.getElementById('logConsole');
const gamesGrid = document.getElementById('gamesGrid');

// DOM Elements - AI Vision Modal Overlay
const visionGameModal = document.getElementById('visionGameModal');
const btnCloseModal = document.getElementById('btnCloseModal');
const modalGameIcon = document.getElementById('modalGameIcon');
const modalGameTitle = document.getElementById('modalGameTitle');
const modalGameCategory = document.getElementById('modalGameCategory');
const modalGameStatus = document.getElementById('modalGameStatus');

const gameVideoFeed = document.getElementById('gameVideoFeed');
const aiOverlayCanvas = document.getElementById('aiOverlayCanvas');
const aiOverlayCtx = aiOverlayCanvas.getContext('2d');
const cameraSourceSelect = document.getElementById('cameraSourceSelect');
const aiTargetBadge = document.getElementById('aiTargetBadge');
const aiTargetName = document.getElementById('aiTargetName');

const modalGameInstructions = document.getElementById('modalGameInstructions');
const modalReceptaclesList = document.getElementById('modalReceptaclesList');
const gameLogConsole = document.getElementById('gameLogConsole');

const btnStartGame = document.getElementById('btnStartGame');
const btnStopGame = document.getElementById('btnStopGame');

// State Variables
let currentXYZ = [0, -163, 212];
let currentNozzleAngle = 0;
let suctionState = false;
let actionSequence = [];
let dragDebounceTimer = null;

let activeGame = null;
let isGameRunning = false;
let cameraStream = null;
let aiAnimFrameId = null;

// Safe Workspace Boundaries
const LIMITS = {
  minX: -180, maxX: 180,
  minY: -280, maxY: 100,
  minZ: 0,    maxZ: 260,
  minRadius: 50, maxRadius: 320
};

// 3 Core Vision & Sensor Games Catalog Details (Exact Repository Files)
const VISION_GAMES_DATA = {
  "color_sorting": {
    "id": "color_sorting",
    "name": "Clasificación por Color (Sensor RGB)",
    "category": "Sensor de Color APDS-9960",
    "icon": "🎨",
    "description": "Detección RGB de bloques con sensor de color y transporte robótico a receptáculos.",
    "instructions": "Ejecuta el código oficial 'Appendix/7.../8. Color Sorting/main.py'. El sensor APDS-9960 detecta la frecuencia RGB del bloque frente al efector final y activa la succión.",
    "receptacles": [
      { "name": "🟥 Receptáculo Rojo", "coords": "(120, -140, 85) mm" },
      { "name": "🟩 Receptáculo Verde", "coords": "(120, -80, 85) mm" },
      { "name": "🟦 Receptáculo Azul", "coords": "(120, -20, 82) mm" }
    ]
  },
  "waste_sorting": {
    "id": "waste_sorting",
    "name": "Clasificación de Residuos (WonderCam IA)",
    "category": "WonderCam AI Vision",
    "icon": "♻️",
    "description": "Reconocimiento por la cámara WonderCam de tarjetas de residuos y separación robótica.",
    "instructions": "Ejecuta el código oficial 'Appendix/12.../Waste Sorting/main.py'. La cámara WonderCam sobre el MaxArm identifica la tarjeta y la coloca en el contenedor correspondiente.",
    "receptacles": [
      { "name": "☣️ Residuos Peligrosos (Izquierda Fondo)", "coords": "(-120, -140, 60) mm" },
      { "name": "📦 Material Reciclable (Izquierda Frente)", "coords": "(-120, -60, 60) mm" },
      { "name": "🍏 Basura Orgánica (Derecha Frente)", "coords": "(120, -60, 60) mm" },
      { "name": "🗑️ Basura General (Derecha Fondo)", "coords": "(120, -140, 60) mm" }
    ]
  },
  "color_tracking_sorting": {
    "id": "color_tracking_sorting",
    "name": "Seguimiento y Ordenamiento por Color",
    "category": "WonderCam AI Vision",
    "icon": "🎯",
    "description": "WonderCam reconoce colores aprendidos, el brazo los sigue con PID y los ordena cuando se detienen.",
    "instructions": "Ejecuta el código oficial 'Appendix/12.../Color Tracking and Sorting/main.py'. Antes de iniciar, aprende rojo, verde y azul exactamente como ID1, ID2 y ID3 en WonderCam. No uses la vista de cámara del PC: sólo deja listo el módulo y coloca el bloque dentro de la zona de reconocimiento.",
    "prerequisite": "WonderCam debe guardar los colores en este orden: ID1=rojo, ID2=verde, ID3=azul. Si los aprendiste azul/rojo/verde, este juego no va a ordenar como se espera.",
    "receptacles": [
      { "name": "🟥 Zona Roja", "coords": "(-120, -140, 85) mm" },
      { "name": "🟩 Zona Verde", "coords": "(-120, -80, 85) mm" },
      { "name": "🟦 Zona Azul", "coords": "(-120, -20, 85) mm" }
    ]
  }
};

// Initialize WebSocket Connection
function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;
  
  logMessage(`[SISTEMA] Conectando WebSocket en ${wsUrl}...`, 'system');
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    logMessage('[SISTEMA] Conexión establecida con el servidor MaxArm.', 'system');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'telemetry') {
      updateTelemetry(data);
    }
  };

  ws.onclose = () => {
    logMessage('[SISTEMA] Conexión cerrada. Reintentando en 3s...', 'error');
    updateStatus(false);
    setTimeout(initWebSocket, 3000);
  };

  ws.onerror = () => {
    logMessage('[ERROR] Error de red WebSocket.', 'error');
  };
}

function updateTelemetry(data) {
  const isConnected = data.is_connected;
  if (data.xyz) {
    currentXYZ = data.xyz;
  }
  suctionState = data.suction || false;

  updateStatus(isConnected, data.port);
  syncUIValues();
  drawArm2D(currentXYZ[0], currentXYZ[1], currentXYZ[2]);
}

function updateStatus(connected, port = 'COM6') {
  if (connected) {
    statusBadge.className = 'status-pill connected';
    statusText.textContent = `Conectado (${port})`;
  } else {
    statusBadge.className = 'status-pill disconnected';
    statusText.textContent = `Desconectado (${port})`;
  }
}

function syncUIValues() {
  txtMetricX.textContent = currentXYZ[0];
  txtMetricY.textContent = currentXYZ[1];
  txtMetricZ.textContent = currentXYZ[2];
  txtMetricNozzle.textContent = `${currentNozzleAngle}°`;

  valX.textContent = `${currentXYZ[0]} mm`;
  valY.textContent = `${currentXYZ[1]} mm`;
  valZ.textContent = `${currentXYZ[2]} mm`;
  valServo.textContent = `${currentNozzleAngle}°`;

  sliderX.value = currentXYZ[0];
  sliderY.value = currentXYZ[1];
  sliderZ.value = currentXYZ[2];
  sliderServo.value = currentNozzleAngle;

  if (suctionState) {
    pumpStatusTag.className = 'pump-status-tag on';
    pumpStatusTag.textContent = 'ENCENDIDA';
    btnToggleSuction.className = 'btn-suction-action suction-on';
    suctionBtnText.textContent = 'APAGAR SUCCIÓN DE VACÍO';
  } else {
    pumpStatusTag.className = 'pump-status-tag off';
    pumpStatusTag.textContent = 'APAGADA';
    btnToggleSuction.className = 'btn-suction-action suction-off';
    suctionBtnText.textContent = 'ENCENDER SUCCIÓN DE VACÍO';
  }

  const j1 = Math.round(90 + (currentXYZ[0] / 180) * 60);
  const j2 = Math.round(90 + ((currentXYZ[2] - 130) / 130) * 45);
  const j3 = Math.round((currentXYZ[1] + 163) / 2);
  badgeJ1.textContent = `J1: ${j1}°`;
  badgeJ2.textContent = `J2: ${j2}°`;
  badgeJ3.textContent = `J3: ${j3}°`;
}

function logMessage(msg, type = 'command') {
  const div = document.createElement('div');
  div.className = `log-entry ${type}`;
  const timestamp = new Date().toLocaleTimeString();
  div.textContent = `[${timestamp}] ${msg}`;
  logConsole.appendChild(div);
  logConsole.scrollTop = logConsole.scrollHeight;
}

function logGameMessage(msg, type = 'command') {
  const div = document.createElement('div');
  div.className = `log-entry ${type}`;
  const timestamp = new Date().toLocaleTimeString();
  div.textContent = `[${timestamp}] ${msg}`;
  gameLogConsole.appendChild(div);
  gameLogConsole.scrollTop = gameLogConsole.scrollHeight;
}

// Check Boundaries
function checkBoundaries(x, y, z) {
  let isLimitReached = false;
  let warningText = '';

  const radius = Math.sqrt(x * x + y * y);

  if (x <= LIMITS.minX || x >= LIMITS.maxX) {
    isLimitReached = true;
    warningText = `Límite Eje X alcanzado (${x} mm). Rango seguro: [-180, 180] mm.`;
  } else if (y <= LIMITS.minY || y >= LIMITS.maxY) {
    isLimitReached = true;
    warningText = `Límite Eje Y alcanzado (${y} mm). Rango seguro: [-280, 100] mm.`;
  } else if (z <= LIMITS.minZ || z >= LIMITS.maxZ) {
    isLimitReached = true;
    warningText = `Límite Eje Z alcanzado (${z} mm). Rango seguro: [0, 260] mm.`;
  } else if (radius < LIMITS.minRadius) {
    isLimitReached = true;
    warningText = `Radio de replegado mínimo alcanzado (${Math.round(radius)} mm).`;
  } else if (radius > LIMITS.maxRadius) {
    isLimitReached = true;
    warningText = `Extensión radial máxima alcanzada (${Math.round(radius)} mm).`;
  }

  if (isLimitReached) {
    criticalLimitMsg.textContent = warningText;
    criticalLimitBox.classList.remove('hidden');
  } else {
    criticalLimitBox.classList.add('hidden');
  }

  const safeX = Math.max(LIMITS.minX, Math.min(LIMITS.maxX, x));
  const safeY = Math.max(LIMITS.minY, Math.min(LIMITS.maxY, y));
  const safeZ = Math.max(LIMITS.minZ, Math.min(LIMITS.maxZ, z));

  return [safeX, safeY, safeZ];
}

function sendPhysicalMove() {
  const reqX = parseInt(sliderX.value);
  const reqY = parseInt(sliderY.value);
  const reqZ = parseInt(sliderZ.value);

  const [safeX, safeY, safeZ] = checkBoundaries(reqX, reqY, reqZ);
  currentXYZ = [safeX, safeY, safeZ];

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      action: 'set_xyz',
      x: safeX,
      y: safeY,
      z: safeZ
    }));
    logMessage(`[XYZ] Movimiento suave a (${safeX}, ${safeY}, ${safeZ}) mm`, 'command');
  }
}

// Sliders Handlers
[sliderX, sliderY, sliderZ].forEach(slider => {
  slider.addEventListener('input', () => {
    const reqX = parseInt(sliderX.value);
    const reqY = parseInt(sliderY.value);
    const reqZ = parseInt(sliderZ.value);

    checkBoundaries(reqX, reqY, reqZ);
    valX.textContent = `${reqX} mm`;
    valY.textContent = `${reqY} mm`;
    valZ.textContent = `${reqZ} mm`;
    txtMetricX.textContent = reqX;
    txtMetricY.textContent = reqY;
    txtMetricZ.textContent = reqZ;

    drawArm2D(reqX, reqY, reqZ);

    clearTimeout(dragDebounceTimer);
    dragDebounceTimer = setTimeout(sendPhysicalMove, 180);
  });

  slider.addEventListener('change', () => {
    clearTimeout(dragDebounceTimer);
    sendPhysicalMove();
  });
});

window.adjustAxis = function(axis, delta) {
  if (axis === 'X') sliderX.value = parseInt(sliderX.value) + delta;
  if (axis === 'Y') sliderY.value = parseInt(sliderY.value) + delta;
  if (axis === 'Z') sliderZ.value = parseInt(sliderZ.value) + delta;

  sendPhysicalMove();
};

btnHome.addEventListener('click', () => {
  currentXYZ = [0, -163, 212];
  sliderX.value = 0;
  sliderY.value = -163;
  sliderZ.value = 212;
  sliderServo.value = 0;
  currentNozzleAngle = 0;
  suctionState = false;

  criticalLimitBox.classList.add('hidden');
  syncUIValues();
  drawArm2D(0, -163, 212);

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action: 'home' }));
    logMessage('[HOME RESET] Solicitud atómica de retorno a posición inicial ejecutada.', 'command');
  }
});

window.setPreset = function(x, y, z) {
  sliderX.value = x;
  sliderY.value = y;
  sliderZ.value = z;
  sendPhysicalMove();
  logMessage(`[PREAJUSTE] Posición fijada a (${x}, ${y}, ${z}) mm.`, 'system');
};

window.adjustServo = function(delta) {
  setServoAngle(currentNozzleAngle + delta);
};

sliderServo.addEventListener('input', (e) => setServoAngle(parseInt(e.target.value)));

function setServoAngle(angle) {
  angle = Math.max(-90, Math.min(90, angle));
  currentNozzleAngle = angle;
  sliderServo.value = angle;
  valServo.textContent = `${angle}°`;
  txtMetricNozzle.textContent = `${angle}°`;

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      action: 'set_servo',
      angle: angle + 90
    }));
  }
}

btnToggleSuction.addEventListener('click', () => {
  suctionState = !suctionState;
  syncUIValues();

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      action: 'suction',
      state: suctionState
    }));
    logMessage(`[BOMBA] Succión de vacío ${suctionState ? 'ACTIVADA' : 'DESACTIVADA'}.`, 'command');
  }
});

btnReconnect.addEventListener('click', () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action: 'reconnect' }));
    logMessage('[CONEXIÓN] Solicitando reconexión a COM6...', 'system');
  }
});

// Action Sequence Table Programmer
btnAddAction.addEventListener('click', () => {
  const stepNum = actionSequence.length + 1;
  const newStep = {
    num: stepNum,
    x: currentXYZ[0],
    y: currentXYZ[1],
    z: currentXYZ[2],
    nozzle: currentNozzleAngle,
    suction: suctionState
  };
  actionSequence.push(newStep);
  renderActionsTable();
  logMessage(`[SECUENCIA] Posición #${stepNum} guardada: (${newStep.x}, ${newStep.y}, ${newStep.z}) mm.`, 'command');
});

btnClearSequence.addEventListener('click', () => {
  actionSequence = [];
  renderActionsTable();
  logMessage(`[SECUENCIA] Secuencia borrada.`, 'system');
});

btnRunSequence.addEventListener('click', async () => {
  if (actionSequence.length === 0) {
    alert('Guarda al menos una posición en la secuencia antes de ejecutar.');
    return;
  }
  logMessage(`[SECUENCIA] Ejecutando rutina de ${actionSequence.length} pasos...`, 'command');

  for (const step of actionSequence) {
    sliderX.value = step.x;
    sliderY.value = step.y;
    sliderZ.value = step.z;
    setServoAngle(step.nozzle);
    suctionState = step.suction;
    sendPhysicalMove();

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: 'suction', state: step.suction }));
    }
    await new Promise(r => setTimeout(r, 1400));
  }
  logMessage(`[SECUENCIA] Rutina completada exitosamente.`, 'command');
});

function renderActionsTable() {
  if (actionSequence.length === 0) {
    actionsTbody.innerHTML = `
      <tr class="empty-row">
        <td colspan="7">No hay posiciones guardadas. Usa "Guardar Posición" para crear una secuencia personalizada.</td>
      </tr>
    `;
    return;
  }

  actionsTbody.innerHTML = '';
  actionSequence.forEach((step, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${step.num}</td>
      <td>${step.x}</td>
      <td>${step.y}</td>
      <td>${step.z}</td>
      <td>${step.nozzle}°</td>
      <td>${step.suction ? '🟢 ON' : '⚪ OFF'}</td>
      <td><button class="btn-step-fine" onclick="removeStep(${idx})">❌</button></td>
    `;
    actionsTbody.appendChild(tr);
  });
}

window.removeStep = function(idx) {
  actionSequence.splice(idx, 1);
  actionSequence.forEach((s, i) => s.num = i + 1);
  renderActionsTable();
};

// ==========================================================================
// VENTANA INDEPENDIENTE & ENUMERACIÓN DE CÁMARA WONDERCAM USB
// ==========================================================================

async function populateCameraDevices() {
  cameraSourceSelect.innerHTML = '';
  
  // Agregar opción por defecto Simulador / WonderCam Stream
  const defaultOpt = document.createElement('option');
  defaultOpt.value = 'synthetic';
  defaultOpt.textContent = 'Simulador / WonderCam Visual Overlay';
  cameraSourceSelect.appendChild(defaultOpt);

  if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
    return;
  }

  try {
    // Pedir permiso temporal para listar etiquetas de cámaras
    await navigator.mediaDevices.getUserMedia({ video: true }).catch(() => {});
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(device => device.kind === 'videoinput');

    videoDevices.forEach((device, idx) => {
      const opt = document.createElement('option');
      opt.value = device.deviceId;

      const label = device.label || `Cámara USB ${idx + 1}`;
      opt.textContent = label.includes('WonderCam') ? `📷 ${label} (Cámara MaxArm)` : label;
      
      // Si la etiqueta contiene WonderCam o USB Camera, seleccionarla automáticamente
      if (label.toLowerCase().includes('wondercam') || label.toLowerCase().includes('usb video')) {
        opt.selected = true;
      }
      cameraSourceSelect.appendChild(opt);
    });

    logGameMessage(`[CÁMARA] ${videoDevices.length} cámaras físicas enumeradas.`, 'system');
  } catch (err) {
    logGameMessage('[CÁMARA] No se detectó cámara física. Usando simulador de video.', 'system');
  }
}

function openVisionModal(gameId) {
  activeGame = VISION_GAMES_DATA[gameId];
  if (!activeGame) return;

  modalGameIcon.textContent = activeGame.icon;
  modalGameTitle.textContent = activeGame.name;
  modalGameCategory.textContent = activeGame.category;
  modalGameInstructions.textContent = activeGame.instructions;

  modalReceptaclesList.innerHTML = '';
  activeGame.receptacles.forEach(rec => {
    const div = document.createElement('div');
    div.className = 'receptacle-item';
    div.innerHTML = `<span class="name">${rec.name}</span><span class="coords">${rec.coords}</span>`;
    modalReceptaclesList.appendChild(div);
  });

  gameLogConsole.innerHTML = '<div class="log-entry system">[SISTEMA] Ventana de control simplificada abierta. No se mostrará cámara en pantalla para este módulo.</div>';
  if (activeGame.prerequisite) {
    logGameMessage(`[PREPARACIÓN] ${activeGame.prerequisite}`, 'system');
  }

  visionGameModal.classList.remove('hidden');
}

btnCloseModal.addEventListener('click', () => {
  stopCameraStream();
  if (aiAnimFrameId) cancelAnimationFrame(aiAnimFrameId);
  visionGameModal.classList.add('hidden');
  isGameRunning = false;
  modalGameStatus.className = 'status-pill disconnected';
  modalGameStatus.textContent = '🔴 DETENIDO';
});

// Camera Stream Handler for Selected Physical Device
async function startCameraStream() {
  const selectedDeviceId = cameraSourceSelect.value;
  stopCameraStream();

  if (selectedDeviceId === 'synthetic') {
    gameVideoFeed.srcObject = null;
    logGameMessage('[CÁMARA] Transmisión en modo Simulador Visual IA activo.', 'system');
    return;
  }

  try {
    const constraints = {
      video: {
        deviceId: selectedDeviceId ? { exact: selectedDeviceId } : undefined,
        width: { ideal: 640 },
        height: { ideal: 480 }
      }
    };
    cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
    gameVideoFeed.srcObject = cameraStream;
    logGameMessage('[CÁMARA] Transmisión en vivo desde la cámara seleccionada (WonderCam USB).', 'system');
  } catch (err) {
    gameVideoFeed.srcObject = null;
    logGameMessage('[CÁMARA] Selecciona la cámara WonderCam conectada al puerto USB de tu PC.', 'error');
  }
}

function stopCameraStream() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }
}

cameraSourceSelect.addEventListener('change', startCameraStream);

// AI Bounding Box & Target Overlay Loop
function startAIBoundingBoxLoop() {
  let simX = 220;
  let simY = 160;
  let dx = 2;

  function renderLoop() {
    aiOverlayCtx.clearRect(0, 0, aiOverlayCanvas.width, aiOverlayCanvas.height);

    if (isGameRunning) {
      simX += dx;
      if (simX > 400 || simX < 140) dx = -dx;

      aiOverlayCtx.strokeStyle = '#06b6d4';
      aiOverlayCtx.lineWidth = 3;
      aiOverlayCtx.strokeRect(simX, simY, 120, 100);

      aiOverlayCtx.fillStyle = '#06b6d4';
      aiOverlayCtx.fillRect(simX, simY - 24, 140, 24);
      aiOverlayCtx.fillStyle = '#000000';
      aiOverlayCtx.font = 'bold 12px JetBrains Mono';
      aiOverlayCtx.fillText('TARGET: WONDERCAM', simX + 6, simY - 8);

      aiOverlayCtx.strokeStyle = '#10b981';
      aiOverlayCtx.lineWidth = 2;
      aiOverlayCtx.beginPath();
      aiOverlayCtx.arc(simX + 60, simY + 50, 10, 0, Math.PI * 2);
      aiOverlayCtx.moveTo(simX + 60, simY + 30);
      aiOverlayCtx.lineTo(simX + 60, simY + 70);
      aiOverlayCtx.moveTo(simX + 40, simY + 50);
      aiOverlayCtx.lineTo(simX + 80, simY + 50);
      aiOverlayCtx.stroke();

      aiTargetBadge.classList.remove('hidden');
      aiTargetName.textContent = activeGame ? `${activeGame.name} (PID Tracking: ${simX}, ${simY})` : 'Target Detected';
    } else {
      aiTargetBadge.classList.add('hidden');
    }

    aiAnimFrameId = requestAnimationFrame(renderLoop);
  }

  renderLoop();
}

// Game Control Buttons: Run Official Repository Script on ESP32
btnStartGame.addEventListener('click', async () => {
  if (!activeGame) return;
  isGameRunning = true;

  modalGameStatus.className = 'status-pill connected';
  modalGameStatus.textContent = '🟢 EJECUTANDO EN VIVO';

  if (activeGame.prerequisite) {
    logGameMessage(`[REQUISITO] ${activeGame.prerequisite}`, 'system');
  }

  logGameMessage(`[CÓDIGO OFICIAL] Enviando script oficial de '${activeGame.name}' al ESP32 por COM6...`, 'command');

  try {
    const res = await fetch(`/api/run_game/${activeGame.id}`, { method: 'POST' });
    const result = await res.json();
    if (result.status === 'ok') {
      logGameMessage(`[CÓDIGO OFICIAL] Carga exitosa: ${result.message}`, 'system');
      logGameMessage(`[RUTA REPOSITORIO] ${result.path}`, 'command');
    } else {
      logGameMessage(`[ERROR CÓDIGO] ${result.message}`, 'error');
    }
  } catch (err) {
    logGameMessage(`[ERROR CONEXIÓN] No se pudo comunicar con el servidor backend.`, 'error');
  }
});

btnStopGame.addEventListener('click', () => {
  isGameRunning = false;
  modalGameStatus.className = 'status-pill disconnected';
  modalGameStatus.textContent = '🔴 DETENIDO';

  logGameMessage(`[DETENIDO] Ejecución del juego detenida por el usuario.`, 'error');

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action: 'stop_game' }));
  }
});

// Load Games Catalog
async function loadGamesCatalog() {
  gamesGrid.innerHTML = '';
  const gamesList = Object.values(VISION_GAMES_DATA);

  gamesList.forEach(game => {
    const card = document.createElement('div');
    card.className = 'game-card';
    card.innerHTML = `
      <div class="game-card-header">
        <div class="game-icon">${game.icon}</div>
        <div>
          <div class="game-category">${game.category}</div>
          <div class="game-title">${game.name}</div>
        </div>
      </div>
      <div class="game-desc">${game.description}</div>
      <button class="btn-game-launch" onclick="openVisionModal('${game.id}')">📷 Abrir Ventana de Visión & Código Oficial</button>
    `;
    gamesGrid.appendChild(card);
  });
}

// 2D Arm Simulation Canvas
function drawArm2D(x, y, z) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const originX = canvas.width / 2;
  const originY = canvas.height - 25;

  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(20, originY);
  ctx.lineTo(canvas.width - 20, originY);
  ctx.stroke();

  const scale = 0.5;
  const targetX = originX + (x * scale);
  const targetY = originY - ((z - 30) * scale);

  const baseH = 35;
  const joint1X = originX;
  const joint1Y = originY - baseH;

  ctx.fillStyle = '#06b6d4';
  ctx.fillRect(originX - 22, originY - baseH, 44, baseH);

  ctx.strokeStyle = '#6366f1';
  ctx.lineWidth = 6;
  ctx.lineCap = 'round';

  ctx.beginPath();
  ctx.moveTo(joint1X, joint1Y);
  const midX = (joint1X + targetX) / 2 - 15;
  const midY = (joint1Y + targetY) / 2 - 25;

  ctx.lineTo(midX, midY);
  ctx.lineTo(targetX, targetY);
  ctx.stroke();

  ctx.fillStyle = '#ffffff';
  ctx.strokeStyle = '#0b0f19';
  ctx.lineWidth = 2;
  [ [joint1X, joint1Y], [midX, midY], [targetX, targetY] ].forEach(([jx, jy]) => {
    ctx.beginPath();
    ctx.arc(jx, jy, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  });

  ctx.fillStyle = suctionState ? '#10b981' : '#ef4444';
  ctx.beginPath();
  ctx.arc(targetX, targetY, 8, 0, Math.PI * 2);
  ctx.fill();
}

// Init
initWebSocket();
loadGamesCatalog();
drawArm2D(0, -163, 212);
