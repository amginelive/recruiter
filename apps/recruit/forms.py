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
        if not self.instance.pk:
            initial = self.initial
            self.company = initial.get('company')

    def save(self, *args, **kwargs):
        job_post = super(JobPostForm, self).save(commit=False)
        skills = self.cleaned_data.get('skills')

        if not self.instance.pk:
            job_post.company = self.company
        job_post.save()

        job_post.skills.clear()
        job_post.skills.set(skills)

        return job_post
