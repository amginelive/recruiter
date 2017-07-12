import json
from tempfile import NamedTemporaryFile

from django.contrib.auth import (
    get_user_model,
)
from django.core.files import File
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G
from PIL import Image

from core.tests import BaseTest
from users.models import UserNote


User = get_user_model()


class FileUploadAPITests(BaseTest):

    def setUp(self):
        super(FileUploadAPITests, self).setUp()

        image = Image.new('RGB', size=(10, 10))
        file = NamedTemporaryFile(suffix='.jpg')
        image.save(file)
        self.image = File(open(file.name, 'rb'))

    def test_candidate_photo_upload(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:profile_photo_upload'),
            {
                'photo': self.image,
                'x': 0,
                'y': 0,
                'width': 10,
                'height': 10,
            }
        )

        self.assertEqual(response.status_code, 200)

        self.candidate.refresh_from_db()

        payload = json.loads(response.content)
        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('image'), self.candidate.photo.url)

    def test_agent_photo_upload(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('users:profile_photo_upload'),
            {
                'photo': self.image,
                'x': 0,
                'y': 0,
                'width': 10,
                'height': 10,
            }
        )

        self.assertEqual(response.status_code, 200)

        self.agent.refresh_from_db()

        payload = json.loads(response.content)
        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('image'), self.agent.photo.url)

    def test_candidate_cv_upload(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:profile_cv_upload'),
            {
                'cv': self.image,
            }
        )

        self.assertEqual(response.status_code, 200)

        self.candidate.refresh_from_db()

        payload = json.loads(response.content)
        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('cv'), self.candidate.cv.url)


class UserNoteAPITests(BaseTest):

    def setUp(self):
        super(UserNoteAPITests, self).setUp()

    def test_valid_create_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:user_note_create'),
            {
                'note_to': self.user_agent.pk,
                'text': 'test note',
                'type': UserNote.TYPE_TEXT,
            }
        )

        self.assertEqual(response.status_code, 200)

        user_note = UserNote.objects.filter(note_to=self.user_agent, note_by=self.user_candidate).first()
        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('data').get('pk'), user_note.pk)

    def test_invalid_create_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:user_note_create'),
            {}
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        self.assertFalse(payload.get('success'))

    def test_valid_update_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=self.user_agent
        )

        response = self.client.post(
            reverse('users:user_note_update', kwargs={'pk': user_note.pk}),
            {
                'note_to': self.user_agent.pk,
                'text': 'test note',
                'type': UserNote.TYPE_TEXT,
            }
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('data').get('pk'), user_note.pk)

    def test_invalid_update_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=self.user_agent
        )

        response = self.client.post(
            reverse('users:user_note_update', kwargs={'pk': user_note.pk}),
            {}
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        self.assertFalse(payload.get('success'))

    def test_delete_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=self.user_agent
        )

        response = self.client.post(reverse('users:user_note_delete', kwargs={'pk': user_note.pk}))

        self.assertEqual(response.status_code, 200)

        user_note = UserNote.objects.filter(note_to=self.user_agent, note_by=self.user_candidate)
        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertFalse(user_note.exists())
