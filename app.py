"""Chatbot sobre comida peruana con Streamlit y Whisper."""
import os
from pathlib import Path

import streamlit as st
from dotenv import dotenv_values
from openai import OpenAI, APIConnectionError, APIStatusError
from openai import AuthenticationError, RateLimitError

from services import answer, transcribe

st.set_page_config(page_title='Sazón Perú', page_icon='🍲', layout='wide')
settings = dotenv_values(Path(__file__).with_name('.env'))


def setting(name, default=''):
    return os.getenv(name) or settings.get(name) or default


def explain_error(error):
    if isinstance(error, AuthenticationError):
        return 'La clave no es válida. Revisa OPENAI_API_KEY en el archivo .env.'
    if isinstance(error, RateLimitError):
        return 'Límite o saldo de la API agotado. Revisa tu cuenta e inténtalo después.'
    if isinstance(error, APIConnectionError):
        return 'No se pudo conectar con OpenAI. Revisa tu conexión e inténtalo otra vez.'
    if isinstance(error, APIStatusError):
        return f'OpenAI devolvió el estado {error.status_code}. Revisa el modelo y el archivo.'
    return str(error)


for key, default in [('messages', []), ('transcript', ''), ('audio_revision', 0)]:
    if key not in st.session_state:
        st.session_state[key] = default

api_key = setting('OPENAI_API_KEY').strip()
model = setting('OPENAI_CHAT_MODEL', 'gpt-4o-mini')
client = OpenAI(api_key=api_key, timeout=60, max_retries=1) if api_key else None

with st.sidebar:
    st.title('🍲 Sazón Perú')
    st.caption('TU COMPAÑERO DE COCINA')
    st.divider()
    st.markdown('### Sabores con historia')
    st.write('Explora recetas, ingredientes y tradiciones de la costa, sierra y selva.')
    st.markdown('**Chat:** ' + model)
    st.markdown('**Voz:** Whisper · español')
    if client:
        st.success('Clave configurada')
    else:
        st.warning('Falta configurar la API')
    st.caption('La clave se lee del archivo .env o del entorno. Nunca se muestra aquí.')
    if st.button('Nueva conversación', use_container_width=True):
        st.session_state.messages = []
        st.session_state.transcript = ''
        st.session_state.audio_revision += 1
        st.rerun()
    st.divider()
    st.caption('Al consultar se envía a OpenAI el texto y hasta 10 turnos anteriores. '
               'El audio se envía solo al pulsar Transcribir. '
               'La aplicación no guarda audios ni conversaciones en disco.')

st.caption('COCINA PERUANA · TEXTO Y VOZ')
st.title('Cada plato tiene una historia')
st.write('Descúbrela, aprende a prepararlo y lleva un poco del Perú a tu mesa.')
if not client:
    st.info('Configura OPENAI_API_KEY en .env y recarga la página para comenzar.')

chat_col, audio_col = st.columns([1.6, 1], gap='large')
question = None
with audio_col:
    with st.container(border=True):
        st.subheader('Tu pregunta, con voz')
        st.caption('1. Graba o sube un audio · 2. Transcribe · 3. Consulta')
        source = st.radio('Origen del audio', ['Subir archivo', 'Grabar micrófono'], horizontal=True)
        if source == 'Subir archivo':
            audio = st.file_uploader(
                'Selecciona un audio (máximo 24 MiB)',
                type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'],
                key=f'upload_{st.session_state.audio_revision}',
            )
        else:
            audio = st.audio_input('Graba tu pregunta', key=f'record_{st.session_state.audio_revision}')
        if audio:
            st.audio(audio)
        if st.button('Transcribir con Whisper', disabled=not client or audio is None,
                     use_container_width=True):
            try:
                with st.spinner('Escuchando tu audio...'):
                    st.session_state.transcript = transcribe(client, audio.name, audio.getvalue())
                st.success('Transcripción lista. Puedes corregirla antes de consultar.')
            except (APIConnectionError, APIStatusError, ValueError) as error:
                st.error(explain_error(error))
        st.text_area('Texto transcrito (editable)', key='transcript', height=130)
        if st.button('Consultar al chatbot', disabled=not client or not st.session_state.transcript.strip(),
                     use_container_width=True):
            question = st.session_state.transcript
        st.download_button('Descargar transcripción', st.session_state.transcript,
                           file_name='transcripcion.txt', mime='text/plain',
                           disabled=not st.session_state.transcript)

with chat_col:
    st.subheader('Conversemos de cocina')
    st.caption('Prueba: «¿Cómo preparo lomo saltado para dos personas?»')
    with st.container(height=440, border=True):
        if not st.session_state.messages:
            with st.chat_message('assistant', avatar='🍲'):
                st.markdown('¡Hola! Soy **Sazón Perú**. Puedo ayudarte con recetas, '
                            'ingredientes y costumbres de la gastronomía peruana. '
                            '¿Qué te gustaría cocinar hoy?')
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
    typed = st.chat_input('Escribe tu pregunta sobre comida peruana...', disabled=not client)
    question = typed or question
    if question and client:
        try:
            with st.spinner('Preparando una respuesta...'):
                response = answer(client, st.session_state.messages, question, model)
            st.session_state.messages.extend([
                {'role': 'user', 'content': question.strip()},
                {'role': 'assistant', 'content': response},
            ])
            st.rerun()
        except (APIConnectionError, APIStatusError, ValueError) as error:
            st.error(explain_error(error))
            st.caption('La consulta no se añadió al historial. Puedes volver a enviarla.')
st.caption('Sazón Perú · Proyecto académico · Streamlit + OpenAI + Whisper')
