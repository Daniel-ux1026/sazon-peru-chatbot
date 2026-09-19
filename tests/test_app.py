from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parents[1] / 'app.py')


def test_missing_key_disables_chat(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    with patch('dotenv.dotenv_values', return_value={}):
        app = AppTest.from_file(APP).run()
    assert not app.exception
    assert app.chat_input[0].disabled


def test_chat_audio_text_and_reset(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key-not-real')
    with patch('services.answer', return_value='El lomo saltado lleva carne, cebolla y tomate.') as mocked:
        app = AppTest.from_file(APP).run()
        app.chat_input[0].set_value('¿Qué lleva el lomo saltado?').run()
        assert not app.exception
        assert len(app.session_state.messages) == 2
        app.text_area[0].set_value('¿Cómo preparo causa limeña?').run()
        next(button for button in app.button if button.label == 'Consultar al chatbot').click().run()
        assert not app.exception
        assert len(app.session_state.messages) == 4
        assert mocked.call_args.args[2] == '¿Cómo preparo causa limeña?'
        next(button for button in app.button if button.label == 'Nueva conversación').click().run()
        assert app.session_state.messages == []
        assert app.session_state.transcript == ''


def test_failed_request_does_not_corrupt_history(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key-not-real')
    with patch('services.answer', side_effect=ValueError('Respuesta vacía')):
        app = AppTest.from_file(APP).run()
        app.chat_input[0].set_value('¿Qué es el ají de gallina?').run()
        assert not app.exception
        assert app.session_state.messages == []
        assert 'Respuesta vacía' in app.error[0].value
