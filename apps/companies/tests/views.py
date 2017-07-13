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


class CompanyInviteViewTests(BaseTest):

    def setUp(self):
        super(CompanyInviteViewTests, self).setUp()

    def test_invalid_update_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_update'),
            {}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('form').errors)

    def test_valid_invite_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_invite'),
            {
                'invitee_email': 'agent2@agent.com',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('companies:company_detail', kwargs={'slug': self.company.slug}))

        company_invitation = CompanyInvitation.objects.filter(invitee_email='agent2@agent.com')

        self.assertTrue(company_invitation.exists())

    def test_invalid_invite_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_invite'),
            {}
        )

        self.assertEqual(response.status_code, 200)

        company_invitation = CompanyInvitation.objects.all()

        self.assertFalse(company_invitation.exists())
