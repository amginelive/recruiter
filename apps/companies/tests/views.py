from tempfile import NamedTemporaryFile

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G
from PIL import Image

from core.tests import BaseTest
from companies.models import (
    Company,
    CompanyInvitation,
)


User = get_user_model()


class CompanyViewTests(BaseTest):

    def setUp(self):
        super(CompanyViewTests, self).setUp()

        image = Image.new('RGB', size=(10, 10))
        file = NamedTemporaryFile(suffix='.jpg')
        image.save(file)
        self.image = File(open(file.name, 'rb'))

    def test_valid_update_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_update'),
            {
                'name': 'agent',
                'domain': 'agent@agent.com',
                'overview': 'agent',
                'description': 'agent',
                'logo': self.image,
                'address_1': 'agent',
                'address_2': 'agent',
                'zip': 'agent',
                'city': 'agent',
                'country': 'PH',
                'website': 'http://www.agent.com',
                'is_charity': True,
                'allow_auto_invite': True,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('company'), self.company)

    def test_invalid_update_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_update'),
            {}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('form').errors)
