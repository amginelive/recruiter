from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.defaultfilters import date
from django.views.generic import (
    CreateView,
    DeleteView,
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
    UserNoteForm,
)
from .mixins import CandidateRequiredMixin
from .models import (
    Candidate,
    UserNote,
)


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


class UserNoteCreateAPIView(LoginRequiredMixin, CreateView, JSONResponseMixin):
    """
    View for adding a note on a user.
    """
    model = UserNote
    form_class = UserNoteForm

    def get_initial(self):
        return {'user': self.request.user}

    def form_valid(self, form):
        user_note = form.save()
        return self.render_json_response({
            'success': True,
            'data': {
                'pk': user_note.pk,
                'note_to': {
                    'pk': user_note.note_to.pk,
                },
                'type': user_note.type,
                'text': user_note.text,
                'created_at': {
                    'proper': date(user_note.created_at, 'D, F d, o P'),
                    'timeago': naturaltime(user_note.created_at),
                },
                'csrf_token': get_token(self.request),
            }
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
        })

user_note_create = UserNoteCreateAPIView.as_view()


class UserNoteUpdateAPIView(LoginRequiredMixin, UpdateView, JSONResponseMixin):
    """
    View for updating a note on a user.
    """
    model = UserNote
    form_class = UserNoteForm

    def get_object(self):
        return UserNote.objects.get(pk=self.kwargs.get('pk'))

    def form_valid(self, form):
        user_note = form.save()
        return self.render_json_response({
            'success': True,
            'data': {
                'pk': user_note.pk,
                'note_to': {
                    'pk': user_note.note_to.pk,
                },
                'type': user_note.type,
                'text': user_note.text,
                'created_at': {
                    'proper': date(user_note.created_at, 'D, F d, o P'),
                    'timeago': naturaltime(user_note.created_at),
                },
            }
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
        })

user_note_update = UserNoteUpdateAPIView.as_view()


class UserNoteDeleteAPIView(LoginRequiredMixin, DeleteView, JSONResponseMixin):
    """
    View for deleting a note on a user.
    """
    model = UserNote

    def get_object(self):
        return UserNote.objects.get(pk=self.kwargs.get('pk'))

    def post(self, request, *args, **kwargs):
        self.get_object().delete()
        return self.render_json_response({'success': True})

user_note_delete = UserNoteDeleteAPIView.as_view()
