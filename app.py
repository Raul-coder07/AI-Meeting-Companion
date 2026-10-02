import os
import warnings
import gradio as gr
from dotenv import load_dotenv
from google import genai
from transformers import pipeline
from transformers.utils import logging as hf_logging

# Desactivar advertencias y logs de transformers
hf_logging.set_verbosity_error()
warnings.filterwarnings("ignore")

# Cargar variables de entorno desde .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY no configurada. Crea el archivo .env basado en .env.example")

# Inicializar cliente de Google Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# Inicializar pipeline de Whisper para Speech-to-Text
print("Cargando modelo Whisper...")
pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny.en",
    chunk_length_s=30,
)

def transcript_and_summarize(audio_file):
    if not audio_file:
        return "Por favor, carga un archivo de audio."

    try:
        # 1. Transcripción con Whisper
        print("Transcribiendo audio con Whisper...")
        transcript_result = pipe(audio_file, batch_size=8)
        transcript_txt = transcript_result["text"]

        # 2. Generación de Puntos Clave con Gemini API
        print("Generando resumen con Gemini...")
        prompt = f"Enumera los puntos clave con detalles del siguiente contexto:\n{transcript_txt}"

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        return response.text

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return f"❌ Error en la ejecución:\n{str(e)}"

# Configuración de la interfaz en Gradio
audio_input = gr.Audio(sources="upload", type="filepath", label="Archivo de audio de la reunión")
output_text = gr.Textbox(label="Transcripción y Puntos Clave")

iface = gr.Interface(
    fn=transcript_and_summarize,
    inputs=audio_input,
    outputs=output_text,
    title="Business AI Meeting Companion 🎙️",
    description="Sube una grabación de audio de tu reunión para obtener automáticamente la transcripción y el desglose de puntos clave."
)

if __name__ == "__main__":
    iface.launch(server_name="127.0.0.1", server_port=7860)