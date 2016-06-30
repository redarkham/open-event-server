import unittest

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from open_event.helpers.data import save_to_db
from open_event.models.user import User
from tests.auth_helper import register
from tests.api.utils import get_path, create_event, create_services, \
    Event, Session
from open_event import current_app as app


class TestTrashedItems404(OpenEventTestCase):
    """
    Test if trashed items return 404 through API
    """

    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'Test@example.com', u'test')
            event_id = create_event(creator_email='Test@example.com')
            create_services(event_id)

    def _test_model(self, name, model):
        # get path
        if name == 'event':
            path = get_path(1)
        elif name == 'user':
            path = '/api/v2/users/1'
        else:
            path = get_path(1, name + 's', 1)
        # check if exists
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 200)
        # delete virtually
        with app.test_request_context():
            item = model.query.get(1)
            item.in_trash = True
            save_to_db(item)
        # get item
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 404)
        self.assertNotIn('Test', resp.data)

    def test_event_api(self):
        self._test_model('event', Event)

    def test_session_api(self):
        self._test_model('session', Session)

    def test_user_api(self):
        self._test_model('user', User)


if __name__ == '__main__':
    unittest.main()
