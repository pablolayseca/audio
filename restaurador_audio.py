import streamlit as st
from pydub import AudioSegment, effects
import noisereduce as nr
import numpy as np
import tempfile
import io

st.set_page_config(page_title="Restaurador de Audio", page_icon="🎵", layout="centered")
st.title("🎵 Restaurador de Audio en Español")

uploaded_file = st.file_uploader("Sube tu archivo de audio", type=["mp3", "wav", "ogg", "flac"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")
    with tempfile.NamedTemporaryFile(delete=False) as tmp_in:
        tmp_in.write(uploaded_file.read())
        tmp_in_path = tmp_in.name

    try:
        audio_seg = AudioSegment.from_file(tmp_in_path)
        audio_seg = effects.normalize(audio_seg)

        # Convertir a numpy para reducción de ruido
        samples = np.array(audio_seg.get_array_of_samples()).astype(np.float32)
        reduced_noise = nr.reduce_noise(y=samples, sr=audio_seg.frame_rate)

        # Crear AudioSegment restaurado
        restored_audio = AudioSegment(
            reduced_noise.tobytes(),
            frame_rate=audio_seg.frame_rate,
            sample_width=audio_seg.sample_width,
            channels=audio_seg.channels
        )

        # Exportar a memoria
        buf = io.BytesIO()
        restored_audio.export(buf, format="mp3")
        buf.seek(0)

        st.success("✅ Restauración completada")
        st.audio(buf, format="audio/mp3")
        st.download_button("⬇️ Descargar audio restaurado", buf, file_name="audio_restaurado.mp3")

    except Exception as e:
        st.error(f"Error procesando el audio: {e}")