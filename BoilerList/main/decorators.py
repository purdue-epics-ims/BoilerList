from django.shortcuts import render
from guardian.shortcuts import get_perms_for_model
from johnslist.settings import REDIRECT_URL
from .models import *
from django.contrib import messages

#general purpose decorator to check if user can access various objects
def user_has_perm(perm):
    def decorator(func):
        def wrapper(request,*args,**kwargs):
            success = False

            user = request.user

            #check if user has perm for Organization

            # if 'organization_id' in kwargs.keys():
            if perm in [p.codename for p in get_perms_for_model(Organization)]:
                organization = Organization.objects.get(id=kwargs['organization_id'])
                if user.has_perm(perm,organization):
                    success = True
                else:
                    code = 1

            #or, check if user has perm for Job

            # elif 'job_id' in kwargs.keys():
            if perm in [p.codename for p in get_perms_for_model(Job)]:
                job = Job.objects.get(id=kwargs['job_id'])
                if user.has_perm(perm,job):
                    success = True
                else:
                    code = 2

            #or, check if user has perm for JobRequest

            # elif 'job_id' in kwargs.keys():
            if perm in [p.codename for p in get_perms_for_model(JobRequest)]:
                job = Job.objects.get(id=kwargs['job_id'])
                jobrequest = JobRequest.objects.get(job_id = kwargs['job_id'],
                                                    organization_id = kwargs['organization_id'])
                if user.has_perm(perm,jobrequest):
                    success = True
                else:
                    code = 3

            #or, check if user has perm for User

            #just check if user id is equal
            elif 'user_id' in kwargs.keys():
                
                if request.user == User.objects.get(id=kwargs['user_id']):
                    success = True
                else:
                    code = 4

            if success == True:
                return func(request,*args,**kwargs)
            else:

                message = "You do not have access to this resource. Error {0}"
                messages.add_message(request, messages.ERROR, message.format(code))
                return render(request,'main/confirm.html')
        return wrapper
    return decorator

#verify user is of type 'communitypartner' or 'purdueuser'
def user_is_type(user_type):
    def decorator(func):
        def wrapper(request,*args,**kwargs):
            message = "You do not have access to this resource. Error {0}"
            #reject anonymous user implicitly
            if request.user.is_anonymous():
                messages.add_message(request, messages.ERROR, message.format(5))
                return render(request,'main/confirm.html')
            is_purdueuser = request.user.userprofile.purdueuser
            if user_type == 'purdueuser':
                if is_purdueuser:
                    return func(request,*args,**kwargs)
                else:
                    messages.add_message(request, messages.ERROR, message.format(6))
                    return render(request,'main/confirm.html')
            elif user_type == 'communitypartner':
                if not is_purdueuser:
                    return func(request,*args,**kwargs)
                else:
                    messages.add_message(request, messages.ERROR, message.format(7))
                    return render(request,'main/confirm.html')
            else:
                raise Exception('User type not recognized')
        return wrapper
    return decorator
