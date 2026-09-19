# Sazón Perú: chatbot gastronómico con voz

Proyecto académico de Python, Streamlit y la API de OpenAI. Responde sobre comida
peruana y convierte audios en texto con **Whisper (`whisper-1`)**. El chat utiliza
**`gpt-4o-mini`**, siguiendo el ejemplo de clase, y conserva contexto de la sesión.

## 1. Requisitos

- Windows con Python 3.11 o superior (probado con Python 3.12).
- Internet y una clave de la API de OpenAI con saldo y acceso a los modelos.
- Para grabar: micrófono y permiso del navegador. En local usa `localhost`;
  un despliegue remoto necesita HTTPS para acceder al micrófono.
- Git y GitHub CLI solamente si deseas publicar el repositorio.

## 2. Instalar en PowerShell

```powershell
cd "C:\Users\DARNEXDAN\Desktop\chatbot\_s06\_tarea"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si `py` no existe, instala Python desde https://www.python.org/downloads/
o usa `python` si ya está disponible. No necesitas activar el entorno virtual.

## 3. Configurar la clave

1. Abre https://platform.openai.com/api-keys e inicia sesión.
2. Pulsa **Create new secret key**, crea una clave y cópiala.
3. Si no tienes `.env`, copia `.env.example` a `.env`.
4. Abre `.env` con Bloc de notas y completa:

```dotenv
OPENAI_API_KEY=pega_aqui_tu_clave
OPENAI_CHAT_MODEL=gpt-4o-mini
```

Guarda el archivo con nombre `.env`, no `.env.txt`. No subas este archivo
a GitHub ni lo incluyas en capturas. `.gitignore` ya lo excluye.
También puedes definir `OPENAI_API_KEY` como variable de entorno;
si existe, tiene prioridad sobre `.env`. El servicio de API tiene consumo
independiente de las suscripciones de ChatGPT.

## 4. Ejecutar

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abre http://localhost:8501. También puedes hacer doble clic en `ejecutar.bat`
después de instalar. Detén el servidor con `Ctrl+C` en su terminal.
Después de cambiar `.env`, recarga la página.

## 5. Probar las dos partes

### Chat de texto

1. Escribe: **¿Cómo preparo lomo saltado para dos personas?**
2. Continúa: **¿Puedo reemplazar la carne por champiñones?**
3. Comprueba que recuerda el plato y adapta la receta.
4. Pregunta por un tema ajeno a la cocina: el asistente debe indicar su especialidad.
5. Usa **Nueva conversación** para borrar el historial y la transcripción.

El alcance se establece mediante instrucciones al modelo; no es un filtro
determinista. La interfaz conserva el historial durante la sesión y envía
los últimos diez turnos completos para limitar el tamaño de cada consulta.

### Audio con Whisper

1. Elige **Subir archivo** o **Grabar micrófono**.
2. Pronuncia: **¿Qué ingredientes lleva la causa limeña?**
3. Pulsa **Transcribir con Whisper**.
4. Revisa y corrige el texto si es necesario.
5. Pulsa **Consultar al chatbot** para usarlo como pregunta.
6. Opcionalmente, descarga la transcripción en TXT.

Formatos: MP3, MP4, MPEG, MPGA, M4A, WAV y WEBM. Máximo: 24 MiB por archivo.
La API puede rechazar un archivo dañado o sin audio aunque su extensión sea válida.
No se transcribe automáticamente al subir: el botón controla cuándo se consume API.
La aplicación no guarda archivos de audio ni conversaciones en disco.

## 6. Archivos

| Archivo | Función |
| --- | --- |
| `app.py` | Interfaz, sesión y mensajes de error |
| `services.py` | Prompt gastronómico, chat y transcripción |
| `.env.example` | Plantilla de configuración sin secretos |
| `.streamlit/config.toml` | Tema visual y límite de carga |
| `requirements.txt` | Dependencias de ejecución |
| `requirements-dev.txt` | Dependencias para las pruebas |
| `tests/` | Pruebas locales con la API simulada |
| `ejecutar.bat` | Inicio rápido en Windows |
| `docs/` | Informe PDF y capturas de ejecución |

## 7. Ejecutar pruebas

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas simulan las respuestas externas: validan el historial, errores,
límites de archivos, selección de Whisper, envío del texto transcrito y reinicio.
No sustituyen una prueba real con saldo y credenciales válidas.

## 8. Publicar en GitHub

Si el repositorio no está publicado aún, desde la carpeta del proyecto:

```powershell
gh auth login
git init -b main
git add .
git commit -m "Implementar chatbot de comida peruana con Whisper"
gh repo create sazon-peru-chatbot --private --source=. --remote=origin --push
gh repo view --web
```

En `gh auth login`, elige GitHub.com, HTTPS y Login with a web browser;
copia el código temporal y autoriza en el navegador.
Si ya existe un repositorio remoto, usa `git push` en lugar de crearlo otra vez.
Un repositorio privado requiere invitar al docente para que pueda revisarlo;
puedes cambiar su visibilidad desde Settings si necesitas un enlace público.

## 9. Problemas frecuentes

- **Falta configurar la API:** revisa nombre y contenido de `.env`.
- **Clave no válida (401):** crea o configura una clave de OpenAI válida.
- **Saldo o límite (429):** revisa facturación y límites en OpenAI Platform.
- **Modelo no disponible:** configura un modelo de chat habilitado para tu cuenta.
- **No se pudo conectar:** revisa Internet, firewall o proxy.
- **Micrófono no disponible:** permite el acceso o utiliza la carga de archivo.
- **Puerto ocupado:** añade `--server.port 8502` al comando de Streamlit.

## Referencias y relación con los ejemplos

Se usaron como guía los tres PDF proporcionados por el docente. Se conserva
el patrón Streamlit + `session_state` + Chat Completions del ejemplo de chat.
El ejemplo de audio muestra Whisper local mediante `faster-whisper`; aquí
se integra Whisper por la API de OpenAI, coherente con la presentación de clase.
La clave se configura fuera del código y las dos funciones se reúnen en una interfaz.

- https://platform.openai.com/docs/api-reference/chat
- https://platform.openai.com/docs/guides/speech-to-text
- https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
- https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input
