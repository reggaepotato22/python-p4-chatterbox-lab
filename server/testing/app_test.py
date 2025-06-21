from datetime import datetime
import pytest

from app import app
from models import db, Message

class TestApp:

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

            assert(hello_from_liza.content == "Hello 👋")
            assert(hello_from_liza.username == "Liza")

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        with app.app_context():
            db.session.add_all([
                Message(content="Hello from Liza", username="Liza"),
                Message(content="Hi brother", username="Duane")
            ])
            db.session.commit()

            response = app.test_client().get('/messages')
            assert response.status_code == 200
            assert response.content_type == 'application/json'

            records = Message.query.all()
            response_json = response.json

            assert isinstance(response_json, list)
            assert len(response_json) == len(records)

            for message_data in response_json:
                assert 'id' in message_data
                assert 'content' in message_data
                assert 'username' in message_data

                matching_record = next((r for r in records if r.id == message_data['id']), None)
                assert matching_record is not None
                assert message_data['content'] == matching_record.content
                assert message_data['username'] == matching_record.username


    def test_creates_new_message_in_the_database(self):
        with app.app_context():
            initial_message_count = Message.query.count()

            app.test_client().post(
                '/messages',
                json={
                    "content":"Hello 👋",
                    "username":"Liza",
                }
            )

            assert Message.query.count() == initial_message_count + 1
            h = Message.query.filter_by(content="Hello 👋").first()
            assert(h)

    def test_returns_data_for_newly_created_message_as_json(self):
        with app.app_context():

            response = app.test_client().post(
                '/messages',
                json={
                    "content":"Hello 👋",
                    "username":"Liza",
                }
            )

            assert(response.status_code == 201)
            assert(response.content_type == 'application/json')

            assert(response.json["content"] == "Hello 👋")
            assert(response.json["username"] == "Liza")


    def test_updates_content_of_message_in_database(self):
        with app.app_context():
            m = Message(content="Original Content", username="TestUser")
            db.session.add(m)
            db.session.commit()
            
            id = m.id

            app.test_client().patch(
                f'/messages/{id}',
                json={
                    "content":"Goodbye 👋",
                }
            )

            g = Message.query.get(id)
            assert(g)
            assert(g.content == "Goodbye 👋")


    def test_returns_data_for_updated_message_as_json(self):
        with app.app_context():
            m = Message(content="Original Content", username="TestUser")
            db.session.add(m)
            db.session.commit()
            
            id = m.id

            response = app.test_client().patch(
                f'/messages/{id}',
                json={
                    "content":"Goodbye 👋",
                }
            )

            assert(response.status_code == 200)
            assert(response.content_type == 'application/json')
            assert(response.json["content"] == "Goodbye 👋")
            assert(response.json["username"] == "TestUser")

    def test_deletes_message_from_database(self):
        with app.app_context():
            hello_from_liza = Message(
                content="Hello 👋",
                username="Liza")
            
            db.session.add(hello_from_liza)
            db.session.commit()

            initial_count = Message.query.count()

            app.test_client().delete(
                f'/messages/{hello_from_liza.id}'
            )

            assert Message.query.count() == initial_count - 1
            h = Message.query.get(hello_from_liza.id)
            assert(not h)