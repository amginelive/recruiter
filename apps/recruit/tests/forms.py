from django.contrib.auth import get_user_model

from django_dynamic_fixture import G

from core.tests import BaseTest
from recruit.forms import (
    JobPostForm,
)
from recruit.models import (
    Skill,
)


User = get_user_model()


class JobPostFormTests(BaseTest):

    def setUp(self):
        super(JobPostFormTests, self).setUp()

        self.skill = G(Skill)

    def test_valid_create_job_post_form(self):
        form = JobPostForm(
            initial={
                'agent': self.agent,
            },
            data={
                'title': 'test',
                'description': 'test',
                'contract': 'test',
                'city': 'test',
                'country': 'PH',
                'skills': [self.skill],
            }
        )

        self.assertTrue(form.is_valid())

        job_post = form.save()

        self.assertTrue(job_post)

    def test_invalid_create_job_post_form(self):
        form = JobPostForm(
            initial={
                'agent': self.agent,
            },
            data={}
        )

        self.assertFalse(form.is_valid())
