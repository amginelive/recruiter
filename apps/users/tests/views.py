from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from core.tests import BaseTest
from companies.models import CompanyInvitation
from recruit.models import (
    Connection,
    ConnectionInvite,
)


User = get_user_model()


class SignupViewTests(BaseTest):

    def setUp(self):
        super(SignupViewTests, self).setUp()

    def test_signup_candidate(self):
        response = self.client.post(
            reverse('account_signup'),
            {
                'email': 'test@candidate.com',
                'first_name': 'candidate',
                'last_name': 'candidate',
                'phone': '+639771234567',
                'account_type': User.ACCOUNT_CANDIDATE,
                'password1': 'password',
                'password2': 'password',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:dashboard'))

        user = User.objects.get(email='test@candidate.com')

        self.assertTrue(user)
        self.assertTrue(user.candidate)

    def test_signup_agent(self):
        response = self.client.post(
            reverse('account_signup'),
            {
                'email': 'test@agent.com',
                'first_name': 'agent',
                'last_name': 'agent',
                'phone': '+639771234567',
                'account_type': User.ACCOUNT_AGENT,
                'password1': 'password',
                'password2': 'password',
            }
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email='test@agent.com')

        self.assertTrue(user)
        self.assertTrue(user.agent)

    def test_signup_connection_invite(self):
        connection_invite = G(
            ConnectionInvite,
            connecter=self.user_candidate,
            connectee_email='test@candidate.com',
        )

        response = self.client.post(
            '{}?invite_type={}&account_type={}&uuid={}&email={}'.format(
                reverse('account_signup'),
                'connection',
                User.ACCOUNT_CANDIDATE,
                connection_invite.uuid,
                connection_invite.connectee_email
            ),
            {
                'email': 'test@candidate.com',
                'first_name': 'candidate',
                'last_name': 'candidate',
                'phone': '+639771234567',
                'account_type': User.ACCOUNT_CANDIDATE,
                'password1': 'password',
                'password2': 'password',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:dashboard'))

        user = User.objects.get(email='test@candidate.com')

        self.assertTrue(user)
        self.assertTrue(user.candidate)

        connection = Connection.objects.filter(
            connecter=connection_invite.connecter,
            connectee=user
        )

        self.assertTrue(connection.exists())

    def test_signup_company_invite(self):
        company_invite = G(
            CompanyInvitation,
            inviter=self.agent,
            invitee_email='test@agent.com',
        )

        response = self.client.post(
            '{}?invite_type={}&account_type={}&uuid={}&email={}'.format(
                reverse('account_signup'),
                'company',
                User.ACCOUNT_AGENT,
                company_invite.uuid,
                company_invite.invitee_email
            ),
            {
                'email': 'test@agent.com',
                'first_name': 'agent',
                'last_name': 'agent',
                'phone': '+639771234567',
                'account_type': User.ACCOUNT_AGENT,
                'password1': 'password',
                'password2': 'password',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:dashboard'))

        user = User.objects.get(email='test@agent.com')

        self.assertTrue(user)
        self.assertTrue(user.agent)
        self.assertEqual(user.agent.company, company_invite.inviter.company)
