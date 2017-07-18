from django.contrib.auth import (
    get_user_model,
    hashers,
)
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from core.tests import BaseTest
from companies.models import (
    Company,
    CompanyInvitation,
    CompanyRequestInvitation,
)
from recruit.models import (
    Connection,
    ConnectionRequest,
)
from users.models import (
    Agent,
    UserNote,
)


User = get_user_model()


class IndexViewTests(BaseTest):

    def setUp(self):
        super(IndexViewTests, self).setUp()

    def test_home_page(self):
        response = self.client.get(reverse('recruit:home'))

        self.assertEqual(response.status_code, 200)

    def test_candidate_dashboard_page(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_agent_dashboard_page(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 200)
