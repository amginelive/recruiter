from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.generic import (
    UpdateView,
    View,
)

from braces.views import (
    JSONResponseMixin,
    LoginRequiredMixin,
)

from .forms import (
    AgentPhotoUploadForm,
    CandidateCVUploadForm,
    CandidatePhotoUploadForm,
    CandidateProfileDetailUpdateForm,
)
from .mixins import CandidateRequiredMixin
from .models import Candidate


User = get_user_model()


class ProfilePhotoUploadAPIView(LoginRequiredMixin, View):
    """
    View for uploading a user's profile picture.
    """
    def post(self, request, **kwargs):
        # show profile dashboard according to user role
        # start with candidate profile
        form_values = request.POST.copy()
        form_values['user'] = request.user.id
        if request.user.account_type == User.ACCOUNT_CANDIDATE:
            candidate = request.user.candidate
            form = CandidatePhotoUploadForm(form_values, request.FILES, instance=candidate)
            if form.is_valid():
                candidate = form.save()
                return JsonResponse({'success': True, 'image': candidate.photo.url})

        # show agent dashboard
        elif request.user.account_type == User.ACCOUNT_AGENT:
            agent = request.user.agent
            form = AgentPhotoUploadForm(form_values, request.FILES, instance=agent)

            if form.is_valid():
                agent = form.save()
                return JsonResponse({'success': True, 'image': agent.photo.url})

profile_photo_upload = ProfilePhotoUploadAPIView.as_view()


class ProfileCVUploadAPIView(CandidateRequiredMixin, View):
    """
    View for uploading a candidate's CV.
    """
    def post(self, request, **kwargs):
        # show profile dashboard according to user role
        # start with candidate profile
        form_values = request.POST.copy()
        form_values['user'] = request.user.id
        candidate = request.user.candidate
        form = CandidateCVUploadForm(form_values, request.FILES, instance=candidate)

        if form.is_valid():
            candidate = form.save(commit=True)
            return JsonResponse({'success': True, 'cv': candidate.cv.url})

profile_cv_upload = ProfileCVUploadAPIView.as_view()


class CandidateProfileDetailUpdateAPIView(CandidateRequiredMixin, UpdateView, JSONResponseMixin):
    """
    View for updating the candidate's profile through the profile page.
    """
    model = Candidate
    form_class = CandidateProfileDetailUpdateForm

    def get_object(self):
        return Candidate.objects.get(pk=self.kwargs.get('pk'))

    def form_valid(self, form):
        form.save()
        return self.render_json_response({
            'success': True,
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
        })

candidate_profile_detail_update = CandidateProfileDetailUpdateAPIView.as_view()
