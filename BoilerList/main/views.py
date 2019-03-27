from django.shortcuts import render,get_object_or_404,redirect
from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_auth
from django.contrib.auth.decorators import login_required
import random
from django.forms.models import inlineformset_factory
from .decorators import user_has_perm, user_is_type
from .forms import *
from guardian.shortcuts import assign_perm
from notifications import notify
from django.core.mail import send_mail
from itertools import chain
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect


def quicksearch(request):
    orgs = Organization.objects.all()
    return render(request,'main/quicksearch.html',
                {'orgs':orgs})

#determine if this is the first time a user has visited a page
def first_visit(user,view):
    # making visited_views into a list and check if this view is in the list
    if view not in user.userprofile.visited_views.split(","):
        # appending a "," because the list is splited by ","
        user.userprofile.visited_views += "{0},".format(view)
        user.userprofile.save()
        return True
    else:
        return False

#login with provided user/pass
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user != None and user.is_active:
            auth_login(request, user)
            #redirect users to page they originally requested
            next = request.POST.get('next')
            if next:
                return HttpResponseRedirect(request.POST.get('next'))
            else:
                return redirect('user_dash')
        else:
            message = "There was a problem with your login.  Please try again."
            messages.add_message(request, messages.ERROR, message)

    return render(request,'main/login.html')

@login_required
def user_dash(request):
    user = request.user
    read_notifications = list(request.user.notifications.read())
    unread_notifications = list(request.user.notifications.unread())
    request.user.notifications.mark_all_as_read()

    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(user,'user_dash')


    if user.username == "Administrator":
        orgs = []
        print(len(Group.objects.all()))
        for group in Group.objects.all():
            try:
                orgs.append(group.organization)
            except Organization.DoesNotExist:
                print("deleted")
                group.delete()                  #DELETE THE GROUP IF IT HAS NO ORGANIZATION (FACULTY PROPOSAL) IN IT

        jobs = Job.objects.all()

        return render(request,
                      'main/administrator_dash.html',
                      {'user_dash': user,
                       'organizations':orgs,
                       'Job': jobs,
                       'unread_notifications':unread_notifications,
                       'read_notifications':read_notifications,
                       'show_dialog':show_dialog
                       })
    elif user.userprofile.purdueuser:

        #orgs = [group.organization for group in user.groups.all()]  THIS DOESNT WORK AFTER DISSOLVING A PROPOSAL, WHEN A PROPOSAL IS DELETED, THE GROUP IS NOT DELETED..
        #                                                            WHEN THE GROUP IS NOT DELETED, IT GIVES ORGANIZATION NOT IN GROUP ERROR...
        #                                                            BELOW CODE IS TO BYPASS THE ERROR, BUT GROUP STILL EXISTS WITHOUT THE PROPOSAL..
        orgs = []
        for group in user.groups.all():
            try:
                orgs.append(group.organization)
            except Organization.DoesNotExist:
                group.delete()                  #DELETE THE GROUP IF IT HAS NO ORGANIZATION (FACULTY PROPOSAL) IN IT

        jobs = Job.objects.all().filter(active=True)
        #print(type(jobs))

        return render(request,
                      'main/purdueuser_dash.html',
                      {'user_dash': user,
                       'organizations':orgs,
                       'Job': jobs,
                       'unread_notifications':unread_notifications,
                       'read_notifications':read_notifications,
                       'show_dialog':show_dialog
                       })
    else:
        jobs = user.jobs.all()
        return render(request, 'main/communitypartner_dash.html',
                     {'user_dash': user,
                       'Job':jobs,
                       'unread_notifications':unread_notifications,
                       'read_notifications':read_notifications,
                       'show_dialog':show_dialog
                     })

#display job information, show jobrequests and their current state
@login_required
@user_is_type('communitypartner')
@user_has_perm('view_job')
def job_dash(request,job_id):
    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(request.user,'job_dash')

    # if request is a POST
    if request.method == 'POST':

        # handle confirm button click
        jobrequest_id = request.POST.get("jobrequest_id","")
        jobrequest = JobRequest.objects.get(id=jobrequest_id)
        if not jobrequest.confirmed and not jobrequest.job.closed:
            jobrequest.confirm()
            message = "You have confirmed this job."
            messages.add_message(request, messages.INFO, message)
        else:
            message = "You have already confirmed this job, or this job is now closed."
            messages.add_message(request, messages.ERROR, message)

    job = Job.objects.get(id=job_id)

    applied_jobrequests = job.jobrequests.order_by('organization').filter(applied = True)

    return render(request, 'main/job_dash.html',
                  {'job': job,
                   'applied_jobrequests': applied_jobrequests,
                   'show_dialog': show_dialog
                   })

#get detailed organization information - email, phone #, users in Org, admins, etc.
def organization_detail(request,organization_id):
    organization = Organization.objects.get(id=organization_id)
    jobs = organization.jobrequests_pending()
    admins = organization.get_admins()
    return render(request, 'main/organization_detail.html',
                {'organization': organization,
                 'jobs':jobs,
                 'admins':admins,
                 'members':organization.group.user_set.all(),
                 })

#display jobs and members of an organization
@login_required
@user_is_type('purdueuser')
@user_has_perm('view_organization')
def organization_dash(request,organization_id):
    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(request.user,'organization_dash')

    org = Organization.objects.get(id=organization_id)
    members = org.group.user_set.all()
    jobrequests = [jr for jr in org.jobrequest_set.all() if jr.confirmed or jr.job.closed == False]
    return render(request, 'main/organization_dash.html',
                  {'organization':org,
                   'members':members,
                   'jobrequests':jobrequests,
                   'show_dialog':show_dialog
                  })


#get detailed info about a jobrequest
@login_required
@user_has_perm('view_jobrequest')
def jobrequest_dash(request,job_id,organization_id):
    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(request.user,'jobrequest_dash')

    job = Job.objects.get(id=job_id)
    organization = Organization.objects.get(id=organization_id)

    # this is the jobrequest for a particular organization
    jobrequest = JobRequest.objects.get(job = job, organization = organization)
    request.session['originalJobrequestID'] = jobrequest.id
    comments = jobrequest.comment_set.all()
    perm_to_edit_jobrequest_state = request.user.has_perm('edit_jobrequest_state',jobrequest)
    form = CommentCreateForm()

    # if request is a POST
    if request.method == 'POST':

        # handle apply button click
        if request.POST.get("action","")=="apply": # change from accept to apply
            if jobrequest.is_pending() and perm_to_edit_jobrequest_state:
                jobrequest.apply()
                message = "You have applied to this job."
                link = request.build_absolute_uri(reverse('jobrequest_dash', kwargs = {'job_id': jobrequest.job.id, 'organization_id': organization_id}))
                send_mail('BoilerConnect - Job Request Accepted', '{0} has applied for your Job Request!. Click on the link to see the request. {1}'.format(organization.name, link),'boilerconnect1@gmail.com', [jobrequest.job.creator.email], fail_silently=False)
                messages.add_message(request, messages.INFO, message)

            else:
                message = "You have applied for this job."
                messages.add_message(request, messages.ERROR, message)

        # handle decline button click
        if request.POST.get("action","")=="notInterested": # change from decline to not interested
            if jobrequest.is_pending() and perm_to_edit_jobrequest_state:
                jobrequest.decline()
                message = "You are not interested in this job."
                messages.add_message(request, messages.INFO, message)
                link = request.build_absolute_uri(reverse('jobrequest_dash', kwargs = {'job_id': jobrequest.job.id, 'organization_id': organization_id}))
                send_mail('BoilerConnect - Job Request Accepted', '{0} is not interested in your Job Request!. Click on the link to see the request. {1}'.format(organization.name, link),'boilerconnect1@gmail.com', [jobrequest.job.creator.email], fail_silently=False)
            else:
                message = "You have already indicated you are not interested."
                messages.add_message(request, messages.ERROR, message)

        # handle confirm button click
        if request.POST.get("action","")=="confirm":
            if not jobrequest.confirmed and not jobrequest.job.closed:
                jobrequest.confirm()
                message = "You have confirmed this job."
                messages.add_message(request, messages.INFO, message)
            else:
                message = "You have already confirmed this job."
                messages.add_message(request, messages.ERROR, message)

        # handle comment button click
        if request.POST.get("action","")=="comment":
            form = CommentCreateForm(request.POST)
            if form.is_valid():
                comment = form.save(commit = False)
                comment.creator = request.user
                comment.jobrequest = jobrequest
                comment.save()

                message = "Comment saved."
                messages.add_message(request, messages.INFO, message)

                # send notification to either Organization or Community partner
                action_object = job
                verb = "commented on"
                if request.user.userprofile.purdueuser:
                    recipient = job.creator
                    link = request.build_absolute_uri(reverse('jobrequest_dash', kwargs = {'job_id': jobrequest.job.id, 'organization_id': organization_id}))
                    send_mail('BoilerConnect - Job Request Accepted', '{0} has commented on your Job Request!. Click on the link to see the comment. {1}'.format(organization.name, link),'boilerconnect1@gmail.com', [jobrequest.job.creator.email], fail_silently=False)
                    url = reverse('job_dash', kwargs={'job_id': job.id})
                else:
                    recipient = jobrequest.organization.group
                    url = reverse('organization_dash', kwargs={'organization_id': organization.id})
                url = url + "?jobrequestID="+str(jobrequest.id)
                notify.send(request.user,
                            verb=verb,
                            action_object=action_object,
                            recipient=recipient,
                            url=url)
            else:
                message = "The comment cannot be empty."
                messages.add_message(request, messages.ERROR, message)
        if request.user.userprofile.purdueuser:
            return HttpResponseRedirect(reverse('organization_dash', kwargs = {'organization_id':organization.id})+ "?jobrequestID="+str(jobrequest.id))
        else:
            return HttpResponseRedirect(reverse('job_dash', kwargs={'job_id': job.id})+ "?jobrequestID="+str(jobrequest.id))
    # if request is GET
    return render(request, 'main/jobrequest_dash.html',
                  {'jobrequest':jobrequest,
                   'comments':comments,
                   'show_dialog':show_dialog,
                   'perm_to_edit_jobrequest_state':perm_to_edit_jobrequest_state,
                   'form':form
                   })

#load the front page with 3 random organizations in the gallery
def front_page(request):
    orgs = Organization.objects.all()
    if(len(orgs) >= 3):
        orgs = random.sample(orgs,3)
        return render(request, 'main/front_page.html',
                      {'active_organization':orgs[0],
                       'organizations':orgs[1:]
                       })
    else:
        return render(request, 'main/front_page.html')

def search(request):
    search_result=[]

    search = request.GET['search'] # the provided search string
    search_model = request.GET['search_model'] # the kind of object returned by the search
    search_by = request.GET['search_by'] # where to apply the search string

    if search_model.lower() == 'organization':
        if search_by.lower() == 'category':
            category = Category.objects.get(name=search)
            search_result = category.organizations.all()
        if search_by.lower() == 'name':
            search_result = Organization.objects.filter(name__icontains=search)
    return render(request,'main/search.html',{'search_result': search_result})

@login_required
@user_has_perm('view_user')
@user_is_type('purdueuser')
def user_membership(request,user_id):
    membership = User.objects.get(id = user_id).groups
    return render(request,'main/user_membership.html',{'membership': membership})

def user_create(request, profile):
    #if user is logged in with an existing account
    if request.user.is_authenticated():
        return redirect('user_dash')

    #if this request was a POST
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = ProfileCreationForm(request.POST)

        #check form validity
        if all([form.is_valid(), profile_form.is_valid()]):
                #creating user and userprofile
                user=form.save()
                profile=profile_form.save()
                profile.user=user
                profile.save()
                user.save()
                form.save_m2m()
                title = "User {0} created".format( user.username )
                confirm = "Thank you for creating an account."

                #automatic login after account creation
                username_auth = request.POST['username']
                password_auth = request.POST['password1']
                login_user = authenticate(username=username_auth, password=password_auth)
                login_auth(request, login_user)
                return redirect('user_dash')
        else:
                return render(request, 'main/user_create.html', {'form':form, 'profile_form':profile_form,'error':"Profile type error."})

#if the request was a GET
    else:
        form = UserCreationForm()
        if(profile == "purdue"):
            profile_form = ProfileCreationForm(initial={'purdueuser': True})
        else:
            profile_form = ProfileCreationForm(initial={'purdueuser': False})

    return render(request, 'main/user_create.html', {'form':form, 'profile_form':profile_form})

@login_required
@user_is_type('purdueuser')
def organization_create(request):
    #If this is the first time the user has visited this page, show a dialog
    show_dialog = first_visit(request.user,'organization_create')
    jobs = Job.objects.all().filter(active=True)
    #if the request was a GET
    if request.method == 'GET':
        form = OrganizationCreateForm()
        

    #if this request was a POST
    elif request.method == 'POST':
        form = OrganizationCreateForm(request.POST, request.FILES)
        print("----------")
        #print(form.)
        print("----------")
        #check form validity
        if form.is_valid() :
            #create new Group + Organization
            organization = form.save(commit=False)
            group = Group.objects.create(name = organization.name)
            organization.group = group
            group.user_set.add(request.user)
            organization.save()
            form.save_m2m()

            message = "Faculty proposal {0} created.".format( organization.name )
            messages.add_message(request, messages.INFO, message)
            return redirect('user_dash')

    return render(request, 'main/organization_create.html', 
                            {'form':form,
                             'show_dialog':show_dialog})

@login_required
def user_settings(request):
        #if this request was a POST and not a GET
    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=request.user)
        profile_form = ProfileCreationForm(request.POST, instance=request.user.userprofile)

        #check form validity
        if all([form.is_valid(), profile_form.is_valid()]):
            #save user to db and store info to 'user'
            user = form.save(commit = False)
            profile=profile_form.save()
            profile.user=user
            profile.save()
            #user.username = request.user.username()
            title = "User {0} modified".format( user.username )
            user.save()

            message = "Your account has been modified."
            messages.add_message(request, messages.INFO, message)

            #logging the user back in
            username_auth = request.POST['username']
            password_auth = request.POST['password1']
            login_user = authenticate(username=username_auth, password=password_auth)
            login_auth(request, login_user)
            return redirect('user_dash')

    #if the request was a GET
    else:
        if request.user.is_authenticated():
            form = UserCreationForm(instance=request.user)
            profile_form = ProfileCreationForm(instance=request.user.userprofile)
        else:
            form = UserCreationForm()
            profile_form = ProfileCreationForm()

    return render(request, 'main/user_settings.html', {'form':form, 'profile_form':profile_form})

@login_required
@user_is_type('purdueuser')
@user_has_perm('edit_organization')
def organization_settings(request, organization_id):
    organization = Organization.objects.get(id=organization_id)
    categories_id = [category.pk for category in organization.categories.all()]
    #if the request was a GET
    if request.method == 'GET':
        modelform = OrganizationEditForm(instance=organization)

    elif request.method == 'POST':
        modelform = OrganizationEditForm(request.POST, instance=organization)

        #check modelform validity
        if modelform.is_valid() :
            #get modelform info
            organization = modelform.save()

            message = "Organization {0} has been modified.".format(organization.name)
            messages.add_message(request, messages.INFO, message)

    return render(request, 'main/organization_settings.html', {'modelform':modelform,'organization' : organization, 'categories_id': categories_id})

@login_required
@user_is_type('communitypartner')
def job_creation(request):

    #if request was POST

    if request.method == 'POST':
        form = JobCreateForm(request.POST)
        # selected_orgs = Organization.objects.filter(pk__in = form.data['organization'])

        #check form validity
        if form.is_valid():
            job = form.save(request)

            message = "Job {0} created".format( job.name )
            messages.add_message(request, messages.INFO, message)
            return redirect('job_dash',job_id=job.id)

    #if the request was a GET

    else:
        category_groups = CategoryGroup.objects.all()
        form = JobCreateForm()

    return render(request, 'main/job_creation.html', {'form':form})

def about(request):
    return render(request, 'main/about.html')

@login_required
@user_is_type('communitypartner')
def job_settings(request,job_id):
    job = Job.objects.get(id=job_id)

    #if the request was a GET
    if request.method == 'GET':
        form = JobEditForm(instance=job)

    elif request.method == 'POST':
        form = JobEditForm(request.POST, instance=job)

        #check form validity
        if form.is_valid():
            #get form info
            job = form.save(request)
            #add new orgs/remove removed orgs here

            message = "Job {0} has been modified.".format(job.name)
            messages.add_message(request, messages.INFO, message)

    return render(request, 'main/job_settings.html', {'form':form,'job' : job})

@login_required
def job_status_update(request):
    status = request.GET['status']
    job_id = request.GET['Jobid']
    if status == 'Active':
        flag = True
    else:
        flag = False
    job = Job.objects.get(pk=job_id)
    try:
        #job = Job.objects.get(pk=job_id)
        job.active = flag
        job.save()
        #write back
        return HttpResponse(status)
    except Exception as e:
        return JsonResponse(status)
    #return render(request, 'main/job_dash.html', {'form':form,'job' : job})

@login_required
def organization_status_update(request):
    status = request.GET['status']
    organization_id = request.GET['Organizationid']
    if status == 'Active':
        flag = True
    else:
        flag = False
    organization = Organization.objects.get(pk=organization_id)
    try:
        organization.active = flag
        organization.save()
        #write back
        return HttpResponse(status)
    except Exception as e:
        return JsonResponse(status)

# for aprroval of project on admin side when it is made
@login_required
def job_approve_update(request):
    status = request.GET['approve']
    job_id = request.GET['Jobid']
    if approve == 'Yes':
        flag = True
    else:
        flag = False
    job = Job.objects.get(pk=job_id)
    try:
        job.approve = flag
        job.save()
        return HttpResponse(status)
    except Exception as e:
        return JsonResponse(status)


@login_required
def delete_job(request):
     job_id = request.GET['Jobid']
     job = Job.objects.get(pk=job_id)
     try:
         job.delete()
         return JsonResponse({'url':'/user'})
     except Exception as e:
         return HttpResponse("deletion not successful")

@login_required
def delete_organization(request):
    organization_id = request.GET['Organizationid']
    organization = Organization.objects.get(pk=organization_id)
    try:
        organization.delete()
        return JsonResponse({'url':'/user'})
    except Exception as e:
        return HttpResponse("deletion not successful")
