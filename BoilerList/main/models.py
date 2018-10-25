from django.db import models
from django.forms import ModelForm,PasswordInput
from django.contrib.auth import forms
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User,Group
from guardian.shortcuts import assign_perm, remove_perm
from notifications.signals import notify
from django.core.urlresolvers import reverse

class UserProfile(models.Model):
    def __unicode__(self):
        return self.user.username

    # UserProfile - User
    user = models.OneToOneField(User,related_name = 'userprofile',null=True, blank = False)
    # purdueuser or communitypartner
    purdueuser = models.BooleanField(default=True, choices=((True, 'Purdue Professor'),(False, 'Community Organization')))
    # save which pages the user has visited before for the purposes of showing helpful dialogs
    visited_views = models.CharField(max_length=64,default="", null=True)
    first = models.CharField('firstname', max_length=128, null=True)
    last = models.CharField('lastname',max_length=128, null=True)
    organization = models.CharField('organization', max_length=128, null=True)
    title = models.CharField('title', max_length=128, null=True)
    phone = models.CharField('phone', max_length=128, null=True)


class CategoryGroup(models.Model):
    def __unicode__(self):
        return self.name

    name = models.CharField('Service Category Group Name',max_length=64)
    description = models.TextField('Service Category Group Description')

class Category(models.Model):
    def __unicode__(self):
        return self.name

    name = models.CharField('Service Category Name',max_length=64)
    description = models.TextField('Service Category Description',null=True)
    group = models.ForeignKey(CategoryGroup,related_name = 'categories')  # Category -= CategoryGroup

class Organization(models.Model):
    def __unicode__(self):
        return self.name

    name = models.CharField('Organization Name',max_length=64)
    #narrative, including learning outcomes and general course description
    description = models.TextField('Organization Description')
    contactinfo = models.CharField('Contact Information',max_length=64, null=True)
    selectedproposal = models.CharField('Selected Community Proposal',max_length=64, null=True)
    #faculty/staff name; course title; department (provide example so they write it out fully, 
    #i.e. Environmental and Ecological Engineering); 
    facultystaffname = models.CharField('Faculty / Staff Name', max_length=64, null=True)
    coursetitle = models.CharField('Course Title', max_length=64, null=True)
    department = models.CharField('Department', max_length=64, null=True)   
    #level (pull down, check all that apply-freshman, sophomore, junior, senior, grad); 
    freshman = models.BooleanField(default = False)
    sophomore = models.BooleanField(default = False)
    junior = models.BooleanField(default = False)
    senior = models.BooleanField(default = False)
    grad = models.BooleanField(default = False)

    categories = models.ManyToManyField(Category, related_name = 'organizations')  # Category =-= Organization
    group = models.OneToOneField(Group) # Organization - Group
    url = models.URLField('Website', blank=True)
    phone_number = models.CharField('Organization phone number',max_length=64)
    icon = models.ImageField(upload_to='organization', null=True)
    available = models.BooleanField(default=True,choices=((True, "Accepting Jobs"),(False, "Not accepting Jobs")))

    class Meta:
        permissions = (
            ( 'view_organization','Can view Organization' ),
            ( 'edit_organization','Can edit Organization' ),
            ( 'is_admin', 'Is an Administrator')
            )

    # get list of jobs accepted for Org
    def jobrequests_accepted(self):
        return JobRequest.objects.filter(organization = self,accepted = True,completed = False)

    # get list of jobs applied to by Org
    def jobrequests_applied(self):
        return JobRequest.objects.filter(organization = self,accepted = False, applied = True)

    # get list of jobs pending for Org
    def jobrequests_pending(self):
        return JobRequest.objects.filter(organization = self,accepted = False,declined = False)

    # get list of jobs declined by Org
    def jobrequests_declined(self):
        return JobRequest.objects.filter(organization = self,accepted = False,declined = True)

    # get list of jobs completed by Org
    def jobrequests_completed(self):
        return JobRequest.objects.filter(organization = self,completed = True)

    # get admins of this org
    def get_admins(self):
        return [user for user in self.group.user_set.all() if user.has_perm('is_admin',self)]


@receiver(post_save, sender=Organization)
def add_perms_organization(sender,**kwargs):
    # check if this post_save signal was generated from a Model create (vs a Model edit)
    if 'created' in kwargs and kwargs['created']:
        organization=kwargs['instance']

        # allow organization to view and edit itself by default
        assign_perm('view_organization',organization.group,organization)
        assign_perm('edit_organization',organization.group,organization)

class Job(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField('Job Name',max_length=128)
    # when the job was created
    date_created = models.DateTimeField('Date Created', auto_now=True)
    # what entity/organization needs this job?
    client_organization = models.CharField('What organization do you represent?', max_length=64)
    # short description
    description = models.TextField('Job Description', max_length=256)
    # end product to be delivered
    deliverable = models.TextField('Deliverable', max_length=256)
    # when Job is due for completion
    duedate = models.DateTimeField('Date Due')
    # all persons who may be affected by project
    #stakeholders = models.TextField('Stakeholders')
    # important technical requirements
    #additional_information = models.TextField('Additional Information', blank = True)
    # budget estimate
    #budget = models.CharField('Budget', max_length=64)
    # file attachments
    #attachments = models.FileField(upload_to='job', blank = True)
    creator = models.ForeignKey(User,related_name = 'jobs')
    organizations = models.ManyToManyField(Organization, through = 'JobRequest', blank=False, null=True)
    #organizations = models.CharField(default="nothing",null=True,max_length = 256)
    contact_information = models.CharField('Contact Information', max_length = 256, blank = False, null=True)
    skill_required = models.CharField('Volunteer skills required', max_length=256, blank = False, null=True)
    hours_day = models.CharField('Number of hours per day', max_length=256, blank = False, null=True)
    #  Job is closed after a jr is confirmed
    closed = models.BooleanField(default = False)
    # some tags to determine what organizations to submit job to
    categories = models.ManyToManyField(Category, related_name = 'jobs')
    #categories = models.CharField(default="nothing",null=True, max_length = 256)
    status = models.IntegerField(default = 0, choices = ((0, 'Pending'), (1, 'Approved'), (2, 'Disapproved'), (3, 'Closed')))
    active = models.BooleanField(default = True)
    approve = models.BooleanField(default = True) # add to admin side, already showing on community agency side
    #checkboxes 
    activism = models.BooleanField(default = False)
    arts = models.BooleanField(default = False)
    civil = models.BooleanField(default = False)
    school = models.BooleanField(default = False)
    crisis = models.BooleanField(default = False)
    criminal = models.BooleanField(default = False)
    disaster = models.BooleanField(default = False)
    economic = models.BooleanField(default = False)
    entrepreneurship = models.BooleanField(default = False)
    environment = models.BooleanField(default = False)
    food = models.BooleanField(default = False)
    housing = models.BooleanField(default = False)
    immigrants = models.BooleanField(default = False)
    individual = models.BooleanField(default = False)
    mental = models.BooleanField(default = False)
    poverty = models.BooleanField(default = False)
    substance = models.BooleanField(default = False)
    STEM = models.BooleanField(default = False)
    transportation = models.BooleanField(default = False)
    veterans = models.BooleanField(default = False)
    voting = models.BooleanField(default = False)
    other = models.CharField('Other categories', max_length=256, blank = True, null=True)
    class Meta:
        permissions = (
            ( 'view_job','Can view Job' ),
            ( 'edit_job','Can edit Job'),
            ( 'is_creator', 'Is a creator of Job')
            )

    # returns JobRequests that have been accepted
    def jobrequests_accepted(self):
        accepted = JobRequest.objects.filter(job = self, accepted = True)
        return accepted
    # returns JobRequests that have been applied to
    def jobrequests_applied(self):
        applied = JobRequest.objects.filter(job = self, accepted = False, applied = True)
        return applied
    # returns JobRequests that are pending
    def jobrequests_pending(self):
        pending = JobRequest.objects.filter(job = self, accepted = False, declined = False, completed = False)
        return pending
    # returns JobRequests that have been declined
    def jobrequests_declined(self):
        declined = JobRequest.objects.filter(job = self, declined = True)
        return declined
    # creates a new JobRequest
    def request_organization(self,organization):
        jr = JobRequest.objects.create(job = self,organization = organization);
        return jr

# add default job permissions
@receiver(post_save, sender=Job)
def add_perms_job(sender,**kwargs):
    # check if this post_save signal was generated from a Model create
    job=kwargs['instance']
    if 'created' in kwargs and kwargs['created']:

        # allow creator to view and edit job
        assign_perm('view_job',job.creator,job)
        assign_perm('edit_job',job.creator,job)
        # allow requested orgs to view job
        for org in job.organizations.all():
            assign_perm('view_job',org.group,job)
    else:
        # notify users of changed JobRequest
        if job.closed:
            jobrequests = job.jobrequests_accepted()
        else:
            jobrequests = job.jobrequests_accepted() | job.jobrequests_pending()
        for jobrequest in jobrequests:
            notify.send(job.creator,
                        verb="modified",
                        action_object=jobrequest,
                        recipient=jobrequest.organization.group,
                        url=reverse('organization_dash',
                                    kwargs = {'organization_id':jobrequest.organization.id})+
                                    "?jobrequestID="+str(jobrequest.id)
                        )


class JobRequest(models.Model):
    def __unicode__(self):
        return self.job.name

    job = models.ForeignKey(Job,related_name = 'jobrequests') # Job -= JobRequest
    organization = models.ForeignKey(Organization)
    applied = models.NullBooleanField(default = False)
    accepted = models.NullBooleanField(default = False)	
    declined = models.NullBooleanField(default = False)
    confirmed = models.NullBooleanField(default = False)
    completed = models.NullBooleanField(default = False)

    class Meta:
            permissions = (
                ( 'view_jobrequest','Can view JobRequest' ),
                ( 'edit_jobrequest','Can edit JobRequest'),
                ( 'edit_jobrequest_state','Can edit JobRequest state'),
                )
    # set a JobRequest as applied
    def apply(self):
        self.accepted = False
        self.applied = True
        self.declined = False
        self.save()
        notify.send(self.organization,
                    verb="applied",
                    action_object=self.job,
                    recipient=self.job.creator,
                    url=reverse('job_dash',
                                kwargs={'job_id': self.job.id}) +
                                "?jobrequestID=" + str(self.id)
                    )
    # set a JobRequest as accepted
    def accept(self):
        self.accepted = True
        self.declined = False
        self.save()
        notify.send(self.organization,
                    verb="accepted",
                    action_object=self.job,
                    recipient=self.job.creator,
                    url=reverse('job_dash',
                                kwargs={'job_id': self.job.id}) +
                                "?jobrequestID=" + str(self.id)
                    )

    # set a JobRequest as pending
    def pend(self):
        self.accepted = False
        self.declined = False
        self.save()
        # shouldn't send a notification to either side of the users.
        # Only superuser should be able to do this.

    # set a JobRequest as declined
    def decline(self):
        self.declined = True
        self.accepted = False
        self.save()
        notify.send(self.organization,
                    verb="declined",
                    action_object=self.job,
                    recipient=self.job.creator,
                    url=reverse('job_dash',
                                kwargs={'job_id': self.job.id}) +
                                "?jobrequestID=" + str(self.id)
                    )

    # set a JobRequest as confirmed
    def confirm(self):
        self.declined = False
        self.accepted = True
        self.confirmed = True
        self.save()
        notify.send(self.organization,
                    verb="confirmed",
                    action_object=self.job,
                    recipient=self.organization.group,
                    url=reverse('organization_dash',
                                kwargs={'organization_id': self.organization.id}) +
                                "?jobrequestID=" + str(self.id)
                    )
        # iterate through all jobrequests in this job and remove permission
        # for other jobrequests
        job = self.job
        job.closed = True
        job.save()
        for jr in job.jobrequests.all():
            if jr != self:
                remove_perm('view_jobrequest',jr.job.creator,jr)
                remove_perm('view_jobrequest',jr.organization.group,jr)
                notify.send(self.organization,
                        verb="has closed the job: ",
                            action_object=self.job,
                            recipient=jr.organization.group,
                            # questionable use of url since user will not have permission to view anymore
                            # url=reverse('organization_dash',
                            #            kwargs={'organization_id': jr.organization.id}) +
                            #            "?jobrequestID=" + str(jr.id)
                            )

   # check if a jobrequest is pending
    def is_pending(self):
        if not self.accepted and not self.declined:
            return True
        else:
            return False

# add default jobrequest permissions
@receiver(post_save, sender=JobRequest)
def jobrequest_save(sender,**kwargs):
    jobrequest=kwargs['instance']
    job = jobrequest.job

    # check if this post_save signal was generated from a Model create
    if 'created' in kwargs and kwargs['created']:

        # allow creator to view and edit jobrequest
        assign_perm('view_jobrequest',job.creator,jobrequest)
        assign_perm('edit_jobrequest',job.creator,jobrequest)
        # allow requested org to view jobrequest
        assign_perm('view_jobrequest',jobrequest.organization.group,jobrequest)
        # allow Purdue user to edit jobrequest state
        assign_perm('edit_jobrequest_state',jobrequest.organization.group,jobrequest)

        # notify users of new JobRequest
        notify.send(job.creator,
                    verb="submitted",
                    action_object=jobrequest,
                    recipient=jobrequest.organization.group,
                    url=reverse('organization_dash',
                                kwargs={'organization_id': jobrequest.organization.id}) +
                                "?jobrequestID=" + str(jobrequest.id)
                    )

# add default jobrequest permissions
@receiver(pre_delete, sender=JobRequest)
def jobrequest_delete(sender,**kwargs):
    jobrequest=kwargs['instance']
    job = jobrequest.job
    # notify users of changed JobRequest
    notify.send(job.creator,
                verb="deleted {0}".format(jobrequest),
                recipient=jobrequest.organization.group)


class Comment(models.Model):
    text_comment = models.TextField('text_comment')
    jobrequest = models.ForeignKey(JobRequest)
    # creator added after form is validated
    creator = models.ForeignKey(User, blank = True, null = True)
    # when comment was made
    created = models.DateTimeField('Created',auto_now_add=True,null=True)
