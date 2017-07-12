from tempfile import NamedTemporaryFile

from django.contrib.auth import get_user_model
from django.core.files import File

from django_dynamic_fixture import G
from PIL import Image

from core.tests import BaseTest
from recruit.models import (
    Skill,
)
from users.forms import (
    AgentUpdateForm,
    AgentPhotoUploadForm,
    CandidateCVUploadForm,
    CandidatePhotoUploadForm,
    CandidateUpdateForm,
    CandidateSettingsForm,
    CVRequestForm,
)
from users.models import (
    Candidate,
    CVRequest,
)


User = get_user_model()


class ProfileFormTests(BaseTest):

    def setUp(self):
        super(ProfileFormTests, self).setUp()

        self.skill = G(Skill)

    def test_candidate_update_form(self):
        form = CandidateUpdateForm(data={
            'phone': '+639771234567',
            'title': 'title',
            'job_type': Candidate.JOB_TYPE_CONTRACT,
            'experience': 10,
            'city': 'city',
            'country': 'PH',
            'desired_city': 'desired city',
            'desired_country': 'PH',
            'willing_to_relocate': True,
            'status': Candidate.STATUS_LOOKING_FOR_CONTRACT,
            'in_contract_status': Candidate.IN_CONTRACT_STATUS_OPEN,
            'out_contract_status': Candidate.OUT_CONTRACT_STATUS_LOOKING,
        })

        self.assertTrue(form.is_valid())

    def test_agent_update_form(self):
        form = AgentUpdateForm(data={
            'phone': '+639771234567',
        })

        self.assertTrue(form.is_valid())


class SettingsFormTests(BaseTest):

    def setUp(self):
        super(SettingsFormTests, self).setUp()

    def test_candidate_settings_form(self):
        form = CandidateSettingsForm(data={
            'auto_cv_download': True,
        })

        self.assertTrue(form.is_valid())


class CVRequestFormTests(BaseTest):
    def setUp(self):
        super(CVRequestFormTests, self).setUp()

    def test_cv_request_form(self):
        form = CVRequestForm(
            data={
                'status': CVRequest.STATUS_PENDING,
            },
            initial={
                'candidate': self.candidate,
                'requested_by': self.user_agent,
            }
        )

        self.assertTrue(form.is_valid())

        cv_request = form.save()

        self.assertEqual(cv_request, CVRequest.objects.filter(candidate=self.candidate, requested_by=self.user_agent).first())


class FileUploadFormTests(BaseTest):

    def setUp(self):
        super(FileUploadFormTests, self).setUp()

        image = Image.new('RGB', size=(10, 10))
        file = NamedTemporaryFile(suffix='.jpg')
        image.save(file)
        self.image = File(open(file.name, 'rb'))

    def test_candidate_photo_upload_form(self):
        form = CandidatePhotoUploadForm(
            data={
                'x': 0,
                'y': 0,
                'width': 10,
                'height': 10,
            },
            files={
                'photo': self.image,
            }
        )

        self.assertTrue(form.is_valid())

    def test_agent_photo_upload_form(self):
        form = AgentPhotoUploadForm(
            data={
                'x': 0,
                'y': 0,
                'width': 10,
                'height': 10,
            },
            files={
                'photo': self.image,
            }
        )

        self.assertTrue(form.is_valid())

    def test_candidate_cv_upload_form(self):
        form = CandidateCVUploadForm(
            files={
                'cv': self.image,
            }
        )

        self.assertTrue(form.is_valid())
