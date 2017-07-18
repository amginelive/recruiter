from django.contrib.auth import (
    get_user_model,
    hashers,
)
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from companies.models import CompanyRequestInvitation
from core.tests import BaseTest
from recruit.models import (
    Connection,
    ConnectionRequest,
    JobReferral,
    UserReferral,
)
from users.models import (
    Agent,
    CVRequest,
)


User = get_user_model()


class IndexViewTests(BaseTest):

    def setUp(self):
        super(IndexViewTests, self).setUp()

    def test_home_page(self):
        response = self.client.get(reverse('recruit:home'))

        self.assertEqual(response.status_code, 200)

    def test_candidate_dashboard_page(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        candidate_to_candidate_network_request = G(
            ConnectionRequest,
            connectee=self.user_candidate,
            connecter=self.user_agent,
            connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK
        )
        candidate_to_candidate_team_member_request = G(
            ConnectionRequest,
            connectee=self.user_candidate,
            connecter=self.user_agent,
            connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER
        )
        candidate_to_agent_network_request = G(
            ConnectionRequest,
            connectee=self.user_candidate,
            connecter=self.user_agent,
            connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_AGENT_NETWORK
        )
        agent_to_agent_network_request = G(
            ConnectionRequest,
            connectee=self.user_candidate,
            connecter=self.user_agent,
            connection_type=ConnectionRequest.CONNECTION_AGENT_TO_AGENT_NETWORK
        )

        candidate_to_candidate_network_connection = G(
            Connection,
            connectee=self.user_candidate,
            connecter=self.user_agent,
            connection_type=Connection.CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK
        )
        candidate_to_candidate_team_member_connection = G(
            Connection,
            connectee=self.user_candidate,
            connecter=self.user_agent,
            connection_type=Connection.CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER
        )
        candidate_to_agent_network_connection = G(
            Connection,
            connectee=self.user_candidate,
            connecter=self.user_agent,
            connection_type=Connection.CONNECTION_CANDIDATE_TO_AGENT_NETWORK
        )
        agent_to_agent_network_connection = G(
            Connection,
            connectee=self.user_candidate,
            connecter=self.user_agent,
            connection_type=Connection.CONNECTION_AGENT_TO_AGENT_NETWORK
        )

        job_referral = G(
            JobReferral,
            referred_to=self.candidate
        )

        candidate_referral = G(
            UserReferral,
            referred_to=self.user_candidate,
            referred_user=self.user_candidate
        )
        agent_referral = G(
            UserReferral,
            referred_to=self.user_candidate,
            referred_user=self.user_agent
        )

        cv_request = G(
            CVRequest,
            candidate=self.candidate,
            status=CVRequest.STATUS_PENDING
        )

        response = self.client.get(reverse('recruit:dashboard'))
        self.assertEqual(response.status_code, 200)

        self.assertIn(candidate_to_candidate_network_request, response.context.get('connection_requests'))
        self.assertIn(candidate_to_candidate_team_member_request, response.context.get('connection_requests'))
        self.assertIn(candidate_to_agent_network_request, response.context.get('connection_requests'))
        self.assertIn(agent_to_agent_network_request, response.context.get('connection_requests'))
        self.assertIn(candidate_to_candidate_network_request, response.context.get('candidate_to_candidate_network_requests'))
        self.assertIn(candidate_to_candidate_team_member_request, response.context.get('candidate_to_candidate_team_member_requests'))
        self.assertIn(candidate_to_agent_network_request, response.context.get('candidate_to_agent_network_requests'))
        self.assertIn(agent_to_agent_network_request, response.context.get('agent_to_agent_network_requests'))

        self.assertIn(candidate_to_candidate_network_connection, response.context.get('candidate_to_candidate_network_connections'))
        self.assertIn(candidate_to_candidate_team_member_connection, response.context.get('candidate_to_candidate_team_member_connections'))
        self.assertIn(candidate_to_agent_network_connection, response.context.get('candidate_to_agent_network_connections'))
        self.assertIn(agent_to_agent_network_connection, response.context.get('agent_to_agent_network_connections'))

        self.assertIn(job_referral, response.context.get('job_referrals'))

        self.assertIn(candidate_referral, response.context.get('candidate_referrals'))
        self.assertIn(agent_referral, response.context.get('agent_referrals'))

        self.assertIn(cv_request, response.context.get('cv_requests'))

    def test_agent_dashboard_page(self):
        self.client.login(username=self.user_agent.email, password='agent')

        candidate_to_candidate_network_request = G(
            ConnectionRequest,
            connectee=self.user_agent,
            connecter=self.user_candidate,
            connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK
        )
        candidate_to_candidate_team_member_request = G(
            ConnectionRequest,
            connectee=self.user_agent,
            connecter=self.user_candidate,
            connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER
        )
        candidate_to_agent_network_request = G(
            ConnectionRequest,
            connectee=self.user_agent,
            connecter=self.user_candidate,
            connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_AGENT_NETWORK
        )
        agent_to_agent_network_request = G(
            ConnectionRequest,
            connectee=self.user_agent,
            connecter=self.user_candidate,
            connection_type=ConnectionRequest.CONNECTION_AGENT_TO_AGENT_NETWORK
        )

        candidate_to_candidate_network_connection = G(
            Connection,
            connectee=self.user_agent,
            connecter=self.user_candidate,
            connection_type=Connection.CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK
        )
        candidate_to_candidate_team_member_connection = G(
            Connection,
            connectee=self.user_agent,
            connecter=self.user_candidate,
            connection_type=Connection.CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER
        )
        candidate_to_agent_network_connection = G(
            Connection,
            connectee=self.user_agent,
            connecter=self.user_candidate,
            connection_type=Connection.CONNECTION_CANDIDATE_TO_AGENT_NETWORK
        )
        agent_to_agent_network_connection = G(
            Connection,
            connectee=self.user_agent,
            connecter=self.user_candidate,
            connection_type=Connection.CONNECTION_AGENT_TO_AGENT_NETWORK
        )

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 200)

        self.assertIn(candidate_to_candidate_network_request, response.context.get('connection_requests'))
        self.assertIn(candidate_to_candidate_team_member_request, response.context.get('connection_requests'))
        self.assertIn(candidate_to_agent_network_request, response.context.get('connection_requests'))
        self.assertIn(agent_to_agent_network_request, response.context.get('connection_requests'))
        self.assertIn(candidate_to_candidate_network_request, response.context.get('candidate_to_candidate_network_requests'))
        self.assertIn(candidate_to_candidate_team_member_request, response.context.get('candidate_to_candidate_team_member_requests'))
        self.assertIn(candidate_to_agent_network_request, response.context.get('candidate_to_agent_network_requests'))
        self.assertIn(agent_to_agent_network_request, response.context.get('agent_to_agent_network_requests'))

        self.assertIn(candidate_to_candidate_network_connection, response.context.get('candidate_to_candidate_network_connections'))
        self.assertIn(candidate_to_candidate_team_member_connection, response.context.get('candidate_to_candidate_team_member_connections'))
        self.assertIn(candidate_to_agent_network_connection, response.context.get('candidate_to_agent_network_connections'))
        self.assertIn(agent_to_agent_network_connection, response.context.get('agent_to_agent_network_connections'))

    def test_agent_dashboard_page_without_company(self):
        user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent2.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        G(
            Agent,
            user=user,
            company=None
        )

        self.client.login(username=user.email, password='agent2')

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('companies:company_create'))

    def test_agent_dashboard_page_without_company_with_existing_domain_auto_invite_activated(self):
        user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        agent = G(
            Agent,
            user=user,
            company=None
        )

        self.client.login(username=user.email, password='agent2')

        self.company.allow_auto_invite = True
        self.company.save()

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('companies:company_invite_success'))

        agent.refresh_from_db()

        self.assertEqual(agent.company, self.company)

    def test_agent_dashboard_page_without_company_with_existing_domain_auto_invite_deactivated(self):
        user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        agent = G(
            Agent,
            user=user,
            company=None
        )

        self.client.login(username=user.email, password='agent2')

        self.company.allow_auto_invite = False
        self.company.save()

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('companies:company_pending'))

        agent.refresh_from_db()
        company_request_invitation = CompanyRequestInvitation.objects.filter(user=user, company=self.company)

        self.assertIsNone(agent.company)
        self.assertTrue(company_request_invitation.exists())
