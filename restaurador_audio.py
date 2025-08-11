
import streamlit as st
from pydub import AudioSegment
import tempfile

st.title("🎵 Restaurador de Audio")
st.write("Sube un archivo de audio y mejora su calidad.")

uploaded_file = st.file_uploader("Elige un archivo de audio", type=["mp3", "wav", "ogg", "flac"])

if uploaded_file:
    # Guardar temporalmente
    with tempfile.NamedTemporaryFile(delete=False) as tmp_in:
        tmp_in.write(uploaded_file.read())
        tmp_in.flush()
        audio_seg = AudioSegment.from_file(tmp_in.name)

    # Ejemplo de "restauración" (solo normalizar volumen)
    restored_audio = audio_seg.apply_gain(-audio_seg.max_dBFS)

    # Guardar archivo restaurado
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_out:
        restored_audio.export(tmp_out.name, format="mp3")
        st.success("✅ Audio restaurado correctamente")
        with open(tmp_out.name, "rb") as file:
            st.download_button("⬇️ Descargar audio restaurado", file, file_name="audio_restaurado.mp3")
