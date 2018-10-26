from django.db import models
from django.forms import ModelForm, CheckboxSelectMultiple
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import*
from django.core.mail import send_mail
from .widgets import *

class OrgForm(ModelForm):
    def save(self, request, commit = True):
        # make the user from the request the creator of the job
        org = super(OrgForm, self).save(commit = False)
        org.creator = request.user
        org.save()

        # make a request to all the new organizations
        # get the organizations we should request from the categories
        category_orgs = Organization.objects.filter(categories__in = job.categories.all())

        level = ""
        if org.freshman:
            level = level + str(org.freshman) + ","
        if org.sophomore:
            level = level + str(org.sophomore) + ","
        if org.junior:
            level = level + str(org.junior) + ","
        if org.senior:
            level = level + str(org.senior) + ","
        if org.grad:
            level = level + str(org.grad) + ","

        #msg = "Project Title:" + str(job.name) + "\n" + "Community Partner & Project Coordinator:" + str(job.client_organization) + "\n" + "Contact Information:" + str(job.contact_information) + "\n" + "Briefly describe the product or service that you expect as a result of this project:" + str(job.deliverable) + "\n" + "Specify the volunteer skill sets required:" + str(job.skill_required) + "\n" + "Specify the date when this project is due. If you are not sure of the exact date, give a close approximation:" + str(job.duedate) + "\n" + "Specify the number of hours the volunteer needs to work per day/week:" + str(job.hours_day) + "\n" + "Give a short description of the job of a volunteer:" + str(job.description) + "\n" + "Categories" + cat
        #send_mail('Boilerlist - New Job Request Submitted', msg, 'boilerconnect1@gmail.com', ['paynel@purdue.edu'], fail_silently = False,)
        return org

#class OrganizationCreateForm(OrgForm):
class OrganizationCreateForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'url', 'description', 'contactinfo', 'selectedproposal', 'facultystaffname', 'coursetitle', 'department', 'freshman', 'sophomore', 'junior', 'senior', 'grad']
        #widgets = {'freshman': CategorySelect()}

#class OrganizationEditForm(OrgForm):
class OrganizationEditForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'url', 'description', 'contactinfo', 'selectedproposal', 'facultystaffname', 'coursetitle', 'department', 'freshman', 'sophomore', 'junior', 'senior', 'grad']

#class OrganizationCreateForm(ModelForm):
#    class Meta:
#        model = Organization
#        fields = ['name', 'url', 'contactinfo', 'description', 'selectedproposal']
#
#class OrganizationEditForm(ModelForm):
#	class Meta:
#		model = Organization
#		fields = ['name', 'url', 'contactinfo', 'description', 'selectedproposal', 'available']

class JobForm(ModelForm):
    def save(self, request, commit = True):
        # make the user from the request the creator of the job
        job = super(JobForm, self).save(commit = False)
        job.creator = request.user
        job.save()

        # save categories
        # normally you would use save_m2m() to save the categories,
        # but the fact that `organizations` is a relation through a model prevents this
        #for cat in self.cleaned_data['categories']:
        #    job.categories.add(cat)

        # make a request to all the new organizations
        # get the organizations we should request from the categories
        category_orgs = Organization.objects.filter(categories__in = job.categories.all())
        
        #for org in self.cleaned_data['organizations'] | category_orgs:
        #    if org not in job.organizations.all():
        #        verb = "submitted"
        #        organization = Organization.objects.get(id = org.pk)
        #        jr = JobRequest.objects.create(organization=organization, job = job)
        #        link = request.build_absolute_uri(reverse('organization_dash', kwargs={'organization_id': org.pk}) + "?jobrequestID=" + str(jr.id))
        #        for user in organization.group.user_set.all():
        #            send_mail('BoilerConnect - New Job submitted', 'There is a job created for your organization. Click on the link to see the request. {0}'.format(link),'boilerconnect1@gmail.com', [user.email], fail_silently=False)
        # '''   
        # do we want the user to be able to delete requests or categories?
        # # remove deleted categories
        # for cat in job.categories.all():
        #     if cat not in self.cleaned_data['categories']:
        #         job.categories.remove(cat)

        # # delete request for all organizations removed
        # for org in job.organizations.all():
        #     if org not in self.cleaned_data['organizations']:
        #         organization = Organization.objects.get(id = org.pk)
        #         jr =  JobRequest.objects.get(organization=organization, job = job).delete()
        #msg = "Project Title:" + str(job.name) + "/n" + "Community Partner & Project Coordinator:" + str(job.client_organization) + "/n" + "Contact Information:" + str(job.contact_information) + "/n" + "Briefly describe the product or service that you expect as a result of this project:" + str(job.deliverable) + "/n" + "Specify the volunteer skill sets required:" + str(job.skill_required) + "/n" + "Specify the date when this project is due. If you are not sure of the exact date, give a close approximation:" + str(job.duedate) + "/n" + "Specify the number of hours the volunteer needs to work per day/week:" + str(job.hours_day) + "/n" + "Give a short description of the job of a volunteer:" + str(job.form.description) + "/n"

        cat = ""
        if job.activism:
            cat = cat + str(job.activism) + ","
        if job.arts:
            cat = cat + str(job.arts) + ","
        if job.civil:
            cat = cat + str(job.civil) + ","
        if job.school:
            cat = cat + str(job.school) + ","
        if job.crisis:
            cat = cat + str(job.crisis) + ","
        if job.criminal:
            cat = cat + str(job.criminal) + ","
        if job.disaster:
            cat = cat + str(job.disaster) + ","
        if job.economic:
            cat = cat + str(job.economic) + ","
        if job.entrepreneurship:
            cat = cat + str(job.entrepreneurship) + ","
        if job.environment:
            cat = cat + str(job.environment) + ","
        if job.food:
            cat = cat + str(job.food) + ","
        if job.housing:
            cat = cat + str(job.housing) + ","
        if job.immigrants:
            cat = cat + str(job.immigrants) + ","
        if job.individual:
            cat = cat + str(job.individual) + ","
        if job.mental:
            cat = cat + str(job.mental) + ","
        if job.poverty:
            cat = cat + str(job.poverty) + ","
        if job.substance:
            cat = cat + str(job.substance) + ","
        if job.STEM:
            cat = cat + str(job.STEM) + ","
        if job.transportation:
            cat = cat + str(job.transportation) + ","
        if job.veterans:
            cat = cat + str(job.veterans) + ","
        if job.voting:
            cat = cat + str(job.voting) + ","
        if job.other:
            cat = cat + str(job.other) + ","    


        #msg = "Project Title:" + str(job.name) + "\n" + "Community Partner & Project Coordinator:" + str(job.client_organization) + "\n" + "Contact Information:" + str(job.contact_information) + "\n" + "Briefly describe the product or service that you expect as a result of this project:" + str(job.deliverable) + "\n" + "Specify the volunteer skill sets required:" + str(job.skill_required) + "\n" + "Specify the date when this project is due. If you are not sure of the exact date, give a close approximation:" + str(job.duedate) + "\n" + "Specify the number of hours the volunteer needs to work per day/week:" + str(job.hours_day) + "\n" + "Give a short description of the job of a volunteer:" + str(job.description) + "\n" + "Categories" + cat
        #send_mail('Boilerlist - New Job Request Submitted', msg, 'boilerconnect1@gmail.com', ['paynel@purdue.edu'], fail_silently = False,)
        return job

class JobCreateForm(JobForm):
    class Meta:
        model = Job
        exclude = ('creator', 'status','organizations','categories')
        widgets = {'categories': CategorySelect()}

class JobEditForm(JobForm):
    class Meta:
        model = Job
        exclude = ('creator','status','organizations','categories')
        widgets = {'categories': CategorySelect()}

class CommentCreateForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('jobrequest',)

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        #fields = ("first","last","organization","title","phone","username", "email", "password1", "password2")
        fields = ("username", "email", "password1", "password2")

class ProfileCreationForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user','visited_views')
        #exclude = ('user','visited_views')