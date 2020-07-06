import pytest
from urlshort import create_app

@pytest.fixture        #used to create testing situation
def app():
    app = create_app()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()