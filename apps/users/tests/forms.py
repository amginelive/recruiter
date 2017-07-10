from django.contrib.auth import get_user_model

from django_dynamic_fixture import G

from core.tests import BaseTest
from recruit.models import (
    Skill,
)
from users.forms import (
    CandidateUpdateForm,
    AgentUpdateForm,
)
from users.models import (
    Candidate,
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
