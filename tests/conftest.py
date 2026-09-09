import pytest
import app as app_module


@pytest.fixture()
def client():
    app_module.app.config['TESTING'] = True
    app_module.CURRENT = {'puzzle': None, 'solution': None}

    with app_module.app.test_client() as client:
        yield client
