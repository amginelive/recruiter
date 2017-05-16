from django import forms

from .models import JobPost


class JobPostForm(forms.ModelForm):
    """
    Form for Job Posts.
    """
    class Meta:
        model = JobPost
        exclude = ('company',)

    def __init__(self, *args, **kwargs):
        super(JobPostForm, self).__init__(*args, **kwargs)
        initial = self.initial
        self.company = initial.get('company')

    def save(self, *args, **kwargs):
        job_post = super(JobPostForm, self).save(commit=False)
        job_post.company = self.company
        job_post.save()

        return job_post
