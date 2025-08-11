import streamlit as st
from pydub import AudioSegment, effects
from pydub.utils import which
import tempfile
import os
import numpy as np
import librosa
import noisereduce as nr
import soundfile as sf
import imageio_ffmpeg

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
AudioSegment.converter = ffmpeg_path

st.set_page_config(page_title="Restaurador de Audio", page_icon="🎵", layout="centered")
st.title("🎵 Restaurador de Audio en Español")
st.markdown("Sube tu audio (wav/mp3/ogg/flac). La app reduce ruido, ecualiza suavemente y normaliza. Mantiene voz y música.")

with st.sidebar:
    st.header("Ajustes")
    noise_reduction_strength = st.slider("Fuerza reducción de ruido", 0.0, 1.0, 0.6, 0.05)
    eq_voice_boost = st.slider("Refuerzo presencia vocal (1x = sin cambio)", 1.0, 2.0, 1.25, 0.05)
    eq_bass_boost = st.slider("Refuerzo graves (1x = sin cambio)", 1.0, 1.5, 1.1, 0.05)
    normalize_toggle = st.checkbox("Normalizar volumen (recomendado)", value=True)
    output_format = st.selectbox("Formato de descarga", ["wav", "mp3"], index=0)

uploaded_file = st.file_uploader("📂 Selecciona un archivo de audio (max 200MB)", type=["wav", "mp3", "ogg", "flac"])

def eq_boost(data, sr, voice_gain=1.25, bass_gain=1.1):
    fft = np.fft.rfft(data)
    freq = np.fft.rfftfreq(len(data), 1.0/sr)
    gain = np.ones_like(freq)
    gain[(freq > 80) & (freq < 250)] *= bass_gain
    gain[(freq > 1000) & (freq < 4000)] *= voice_gain
    gain[freq > 12000] *= 0.95
    boosted = np.fft.irfft(fft * gain)
    return np.real(boosted)

if uploaded_file:
    st.info("Guardando y preparando el audio...")
    tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
    tmp_in.write(uploaded_file.read())
    tmp_in.flush()

    audio_seg = AudioSegment.from_file(tmp_in.name)
    wav_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio_seg.export(wav_temp.name, format="wav")

    st.info("Cargando audio para procesamiento...")
    y, sr = librosa.load(wav_temp.name, sr=None, mono=True)

    st.info("Aplicando reducción de ruido...")
    try:
        reduced = nr.reduce_noise(y=y, sr=sr, prop_decrease=noise_reduction_strength)
    except Exception:
        reduced = nr.reduce_noise(y=y, sr=sr)

    st.info("Aplicando ecualización (voz y música)...")
    eqed = eq_boost(reduced, sr, voice_gain=eq_voice_boost, bass_gain=eq_bass_boost)

    proc_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(proc_tmp.name, eqed, sr)

    processed_seg = AudioSegment.from_file(proc_tmp.name).set_frame_rate(audio_seg.frame_rate)

    if audio_seg.channels == 2:
        processed_seg = AudioSegment.from_mono_audiosegments(processed_seg, processed_seg)

    if normalize_toggle:
        processed_seg = effects.normalize(processed_seg)

    out_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}")
    processed_seg.export(out_tmp.name, format=output_format)

    st.subheader("Antes / Después")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Antes")
        st.audio(wav_temp.name)
    with col2:
        st.write("Después")
        st.audio(out_tmp.name)

    with open(out_tmp.name, "rb") as f:
        suggested_name = f"audio_restaurado.{output_format}"
        st.download_button("⬇️ Descargar audio restaurado", data=f.read(), file_name=suggested_name, mime=f"audio/{output_format}")

    try:
        os.unlink(tmp_in.name)
        os.unlink(wav_temp.name)
        os.unlink(proc_tmp.name)
        os.unlink(out_tmp.name)
    except Exception:
        pass
