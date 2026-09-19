from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from services import MAX_AUDIO_BYTES, SYSTEM_PROMPT, answer, transcribe


def test_chat_preserves_context_and_specialty():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='Usa champiñones.'))]
    )
    history = [{'role': 'user', 'content': 'Quiero lomo saltado vegetariano.'},
               {'role': 'assistant', 'content': 'Podemos adaptar la receta.'}]
    assert answer(client, history, '¿Con qué reemplazo la carne?', 'gpt-4o-mini') == 'Usa champiñones.'
    sent = client.chat.completions.create.call_args.kwargs['messages']
    assert sent[0] == {'role': 'system', 'content': SYSTEM_PROMPT}
    assert sent[1:3] == history
    assert len(history) == 2


@pytest.mark.parametrize('question', ['', '   ', 'x' * 4001])
def test_invalid_questions_do_not_call_api(question):
    client = MagicMock()
    with pytest.raises(ValueError):
        answer(client, [], question, 'gpt-4o-mini')
    client.chat.completions.create.assert_not_called()


def test_transcription_uses_whisper_and_returns_text():
    client = MagicMock()
    client.audio.transcriptions.create.return_value = ' ¿Cómo preparo causa limeña? '
    assert transcribe(client, 'pregunta.wav', b'audio-test') == '¿Cómo preparo causa limeña?'
    params = client.audio.transcriptions.create.call_args.kwargs
    assert params['model'] == 'whisper-1'
    assert params['language'] == 'es'
    assert params['file'] == ('pregunta.wav', b'audio-test')


@pytest.mark.parametrize('name,data', [
    ('audio.wav', b''), ('archivo.exe', b'abc'),
    ('audio.mp3', b'x' * (MAX_AUDIO_BYTES + 1)),
], ids=['empty', 'unsupported', 'oversize'])
def test_invalid_audio_never_reaches_api(name, data):
    client = MagicMock()
    with pytest.raises(ValueError):
        transcribe(client, name, data)
    client.audio.transcriptions.create.assert_not_called()


def test_empty_transcription_is_rejected():
    client = MagicMock()
    client.audio.transcriptions.create.return_value = ' '
    with pytest.raises(ValueError):
        transcribe(client, 'audio.wav', b'audio-test')
