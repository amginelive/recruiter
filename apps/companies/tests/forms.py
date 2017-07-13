import shutil
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File

from django_dynamic_fixture import G
from PIL import Image

from core.tests import BaseTest
from companies.forms import (
    CompanyUpdateForm,
)
from companies.models import (
    Company,
    CompanyInvitation,
)


User = get_user_model()


class CompanyFormTests(BaseTest):

    def setUp(self):
        super(CompanyFormTests, self).setUp()

        image = Image.new('RGB', size=(1, 1))
        file = NamedTemporaryFile(suffix='.jpg')
        new_file_name = settings.MEDIA_ROOT + '/comic.jpg'
        shutil.copy(file.name, new_file_name)
        image.save(new_file_name)
        self.image = File(open(new_file_name, 'rb'))

    def test_valid_update_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        form = CompanyUpdateForm(
            instance=self.company,
            data={
                'name': 'agent',
                'domain': 'agent@agent.com',
                'overview': 'agent',
                'description': 'agent',
                'address_1': 'agent',
                'address_2': 'agent',
                'zip': 'agent',
                'city': 'agent',
                'country': 'PH',
                'website': 'http://www.agent.com',
                'is_charity': True,
                'allow_auto_invite': True,
            },
            files={
                'logo': self.image,
            }
        )

        self.assertTrue(form.is_valid())

        company = form.save()

        self.assertTrue(company)

    def test_invalid_update_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        form = CompanyUpdateForm(
            instance=self.company,
            data={},
            files={}
        )

        self.assertFalse(form.is_valid())
