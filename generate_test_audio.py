"""
Genera un archivo WAV de prueba con tono sinusoidal.
Se usa para verificar que la API de Groq responde correctamente.
"""
import struct
import wave
import math
import os

output_path = os.path.join(os.path.dirname(__file__), "test_audio.wav")

# Parámetros
sample_rate = 16000
duration = 3  # segundos
frequency = 440  # Hz (La4)

n_samples = sample_rate * duration
samples = []
for i in range(n_samples):
    t = i / sample_rate
    value = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * t))
    samples.append(struct.pack('<h', value))

with wave.open(output_path, 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(samples))

print(f"Archivo creado: {output_path}")
print(f"Tamaño: {os.path.getsize(output_path) / 1024:.1f} KB")
print(f"Duración: {duration}s | Sample rate: {sample_rate} Hz")
