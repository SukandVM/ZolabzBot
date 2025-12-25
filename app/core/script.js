const IMAGE_INTERVAL_MS = 42;
const AUDIO_INTERVAL_MS = 3000; // Record 3 seconds of audio at a time

const drawFaceRectangles = (video, canvas, faces) => {
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "#49fb35";
    ctx.lineWidth = 2;
    
    for (const [x, y, width, height] of faces.faces) {
        ctx.beginPath();
        ctx.rect(x, y, width, height);
        ctx.stroke();
    }
};

const updateStatus = (type, connected) => {
    const indicator = document.getElementById(`status-indicator-${type}`);
    const text = document.getElementById(`status-text-${type}`);
    const startBtn = document.getElementById('button-start');
    const stopBtn = document.getElementById('button-stop');
    const label = type === 'video' ? 'Video' : 'Audio';
    
    if (connected) {
        indicator.className = 'status-indicator status-connected';
        text.textContent = `${label}: Connected`;
        if (type === 'video') {
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
        }
    } else {
        indicator.className = 'status-indicator status-disconnected';
        text.textContent = `${label}: Disconnected`;
        if (type === 'video') {
            startBtn.style.display = 'block';
            stopBtn.style.display = 'none';
        }
    }
};

const addTranscription = (text, language) => {
    if (!text || text.trim() === '') return;
    
    const container = document.getElementById('transcriptions');
    if (container.querySelector('.text-muted')) {
        container.innerHTML = '';
    }
    
    const item = document.createElement('div');
    item.className = 'transcription-item';
    item.innerHTML = `
        <div class="transcription-text">${text}</div>
        <div class="transcription-time">${new Date().toLocaleTimeString()} • ${language}</div>
    `;
    container.insertBefore(item, container.firstChild);
    
    // Keep only last 10 transcriptions
    while (container.children.length > 10) {
        container.removeChild(container.lastChild);
    }
};

const startFaceDetection = (video, canvas, deviceId) => {
    const socket = new WebSocket('ws://localhost:8000/face-detection');
    let intervalId;
    const captureCanvas = document.createElement('canvas');
    const captureCtx = captureCanvas.getContext('2d');
    
    socket.addEventListener('open', function() {
        console.log('WebSocket connected successfully');
        updateStatus('video', true);
        
        navigator.mediaDevices.getUserMedia({
            audio: false,
            video: {
                deviceId,
                width: { max: 640 },
                height: { max: 480 },
            },
        }).then(function(stream) {
            video.srcObject = stream;
            video.play().then(() => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                captureCanvas.width = video.videoWidth;
                captureCanvas.height = video.videoHeight;
                
                intervalId = setInterval(() => {
                    captureCtx.drawImage(video, 0, 0);
                    captureCanvas.toBlob((blob) => {
                        if (socket.readyState === WebSocket.OPEN) {
                            socket.send(blob);
                        }
                    }, 'image/jpeg');
                }, IMAGE_INTERVAL_MS);
            });
        }).catch(err => {
            console.error('Camera access error:', err);
            alert('Failed to access camera: ' + err.message);
        });
    });
    
    socket.addEventListener('message', function(event) {
        drawFaceRectangles(video, canvas, JSON.parse(event.data));
    });
    
    socket.addEventListener('close', function(event) {
        console.log('WebSocket closed:', event.code, event.reason);
        updateStatus('video', false);
        window.clearInterval(intervalId);
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }
        video.pause();
    });
    
    socket.addEventListener('error', function(err) {
        console.error('WebSocket error:', err);
        alert('Failed to connect to face detection server. Make sure the server is running on ws://localhost:8000/face-detection');
    });
    
    return socket;
};

const startSpeechRecognition = () => {
    const socket = new WebSocket('ws://localhost:8000/speech-recognition');
    let mediaRecorder;
    let audioChunks = [];
    
    socket.addEventListener('open', function() {
        console.log('Speech recognition WebSocket connected');
        updateStatus('audio', true);
        
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = () => {
                    if (audioChunks.length > 0) {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        if (socket.readyState === WebSocket.OPEN) {
                            socket.send(audioBlob);
                        }
                        audioChunks = [];
                    }
                    
                    // Restart recording if socket still open
                    if (socket.readyState === WebSocket.OPEN) {
                        setTimeout(() => {
                            if (mediaRecorder && mediaRecorder.state === 'inactive') {
                                mediaRecorder.start();
                                setTimeout(() => mediaRecorder.stop(), AUDIO_INTERVAL_MS);
                            }
                        }, 100);
                    }
                };
                
                // Start recording
                mediaRecorder.start();
                setTimeout(() => mediaRecorder.stop(), AUDIO_INTERVAL_MS);
            })
            .catch(err => {
                console.error('Microphone access error:', err);
                alert('Failed to access microphone: ' + err.message);
            });
    });
    
    socket.addEventListener('message', function(event) {
        const data = JSON.parse(event.data);
        if (data.text && data.text.trim()) {
            addTranscription(data.text, data.language);
        }
    });
    
    socket.addEventListener('close', function() {
        console.log('Speech recognition WebSocket disconnected');
        updateStatus('audio', false);
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
        if (mediaRecorder && mediaRecorder.stream) {
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    });
    
    return { socket, getRecorder: () => mediaRecorder };
};

window.addEventListener('DOMContentLoaded', (event) => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const cameraSelect = document.getElementById('camera-select');
    const stopBtn = document.getElementById('button-stop');
    const enableSpeech = document.getElementById('enable-speech');
    let videoSocket, audioConnection;
    
    // Request camera permissions and enumerate devices
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            // Stop the stream immediately, we just needed permission
            stream.getTracks().forEach(track => track.stop());
            return navigator.mediaDevices.enumerateDevices();
        })
        .then((devices) => {
            for (const device of devices) {
                if (device.kind === 'videoinput' && device.deviceId) {
                    const deviceOption = document.createElement('option');
                    deviceOption.value = device.deviceId;
                    deviceOption.innerText = device.label || `Camera ${cameraSelect.options.length}`;
                    cameraSelect.appendChild(deviceOption);
                }
            }
        })
        .catch(err => {
            console.error('Camera permission/enumeration error:', err);
            alert('Please allow camera access to use this application');
        });
    
    document.getElementById('form-connect').addEventListener('submit', (event) => {
        event.preventDefault();
        
        if (videoSocket) {
            videoSocket.close();
        }
        if (audioConnection) {
            audioConnection.socket.close();
        }
        
        const deviceId = cameraSelect.selectedOptions[0]?.value;
        if (deviceId) {
            videoSocket = startFaceDetection(video, canvas, deviceId);
            
            if (enableSpeech.checked) {
                audioConnection = startSpeechRecognition();
            }
        } else {
            alert('Please select a camera first');
        }
    });
    
    stopBtn.addEventListener('click', () => {
        if (videoSocket) {
            videoSocket.close();
            videoSocket = null;
        }
        if (audioConnection) {
            audioConnection.socket.close();
            audioConnection = null;
        }
    });
});