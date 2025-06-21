import pytest
from app import app
from models import db, Message

class TestMessage:

    @pytest.fixture(autouse=True)
    def setup_app_context(self):
        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_has_correct_columns(self):
        with app.app_context():
            hello_from_liza = Message(
                content="Hello 👋",
                username="Liza"
            )
            db.session.add(hello_from_liza)
            db.session.commit()

            retrieved_message = Message.query.first()
            assert retrieved_message.content == "Hello 👋"
            assert retrieved_message.username == "Liza"
            assert repr(retrieved_message) == f'<Message {retrieved_message.id}: {retrieved_message.username} - {retrieved_message.content}>'