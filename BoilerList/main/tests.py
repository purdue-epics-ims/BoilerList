from main.models import *
from django.test import TestCase
from django.core.files import File
from django.core.urlresolvers import reverse
from johnslist.settings import PIC_POPULATE_DIR
from main.forms import*
#for login test
from django.contrib.auth.models import AnonymousUser

from django.test import Client

'''
    todo:  [x] - group tests by model they test

    User:
        Interface:
            [x] - login
            [x] - user_create
            [x] - user_edit
            [x] - user_job_index
            [] - permissions on views (user,job, org)

    Job:
        Backend:
            [x] - default permissions (creator has perms, accepted/pending have perms)
            [x] - request_organization (check requested/accepted relation exists)
            [x] - jobrequests_accepted (use request_organization)
            [x] - jobrequests_pending (use request_organization)
            [x] - jobrequests_declined (use request_organization)
        Interface:
            [x] - job_creation (check job exists, check default perms, check requested orgs)
            [ ] - job_creation (check job submitted to groups in categories)
            [x] - jobrequest_dash (check response.context['job'] is the same that was created)

    Organization:
        Backend:
            [x] - default permissions (admin has perms, members have perms)
            [x] - jobs_accepted
            [x] - jobs_pending
            [x] - jobs_declined
            [x] - jobs_completed
            [x] - get_admins
        Interface:
            [x] - org_detail
            [] - org accept/decline jobs
            [x] - organization create
            [] - organization edit
'''



#login as user with provided password and return response
def login_as(self,user,password):
    return self.client.post(reverse("login"),{'username':user,'password':password},follow=True)

def logout(self):
    return self.client.get(reverse('logout'))

#generic setup for all testcases
def set_up(self):
        #create users
        self.u_pu = User.objects.create(username='foobar_purdueuser')
        self.u_pu.set_password('asdf')
        self.u_pu.save()
        UserProfile.objects.create(user = self.u_pu, purdueuser = True)

        self.u_cp = User.objects.create(username='foobar_communitypartner')
        self.u_cp.set_password('asdf')
        self.u_cp.save()
        UserProfile.objects.create(user = self.u_cp, purdueuser = False)
        #create category owned by foobar_purdueuser
        self.cat_g = CategoryGroup.objects.create(name='foobar_category_group',description="test_description group")
        self.cat = Category.objects.create(name='foobar_category',description="test description",group = self.cat_g)
        self.j = Job.objects.create(name='foobar_job',description="test description",duedate='2015-01-01',creator=self.u_cp)
        #create group/org
        self.g=Group.objects.create(name="foobar_group")
        self.g.user_set.add(self.u_pu)
        self.o = Organization.objects.create(name = self.g.name, group = self.g, description="test description",phone_number="123-456-7890")
        self.o.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')
        # create another group & org that has the `self.cat` category
        self.g2=Group.objects.create(name="foobar2_group")
        self.g2.user_set.add(self.u_pu)
        self.o2 = Organization.objects.create(name = self.g2.name, group = self.g2, description="test description",phone_number="123-456-7890")
        self.o2.categories.add(self.cat)
        self.o2.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')

class UserTestCase(TestCase):
    #django calls this initialization function automatically
    def setUp(self):
        set_up(self)
        self.u2 = User.objects.create(username='foobar_user1')
        self.u2.set_password('asdf')
        self.u2.save()

    ### Interface Tests ###

    def test_login(self):
        #Test for login failure
        response = login_as(self,'invalid_user0','password')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('error' in list(response.context['messages'])[0].tags)

        #Test successful login
        response = login_as(self,self.u_pu.username,'asdf')
        #check redirect
        self.assertRedirects(response,reverse('user_dash'))
        #check logged in as user0
        response = self.client.get(reverse('front_page'))
        self.assertEqual(response.context['user'],self.u_pu)

        #Test logout
        response = logout(self)
        self.assertNotEqual(response.context['user'],self.u_pu)

    def test_user_create(self):
        #successful user creation
        response = self.client.post(reverse('user_create', kwargs={'profile': "purdue"}), {'username': 'user', 'password1':'zxcv', 'password2':'zxcv', 'user_type': 'purdue','email':'evan@evanw.org'})
        self.assertTrue(User.objects.get(username='user'))
        #unsuccessful user creation
        response = self.client.post(reverse('user_create', kwargs={'profile': "purdue"}), {'username': 'user_fail', 'password1':'zxcv', 'password2':'zxcvhg'})
        self.assertEqual(0,len(User.objects.filter(username='user_fail')))

    def test_user_edit(self):
        response = self.client.post(reverse('user_settings'))
        self.assertTrue(response.status_code == 302)
        login_as(self, self.u_pu.username, 'asdf')
        response = self.client.post(reverse('user_settings'))
        self.assertTrue(response.status_code == 200)
        #change the users username, then try to log in again

    def test_view_permissions(self):
        #verify user is redirected
        response = self.client.get(reverse('user_dash'))
        self.assertRedirects(response,'/login?next='+reverse('user_dash'))
        login_as(self,self.u_pu.username,'asdf')
        #verify user can view their own detail page
        response = self.client.get(reverse('user_dash',))
        self.assertTrue(len(response.context['messages']) == 0)
        self.assertTrue(response.status_code == 200)

class JobTestCase(TestCase):
    #django calls this initialization function automatically
    def setUp(self):
        set_up(self)
        self.j2 = Job.objects.create(name='test_job',description="test description",duedate='2015-01-01',creator=self.u_cp)

    ### Backend Tests ###

    #ensure job is editable by creator 
    def test_permissions(self):
        self.assertTrue(self.u_cp.has_perm('edit_job',self.j))
        self.assertTrue(self.u_cp.has_perm('view_job',self.j))

    #check creating a jobrequest
    def test_request_organization(self):
        jr = self.j.request_organization(self.o)
        self.assertIsInstance(jr,JobRequest)

    #check if accepted job requets are returned
    def test_jobrequests_accepted(self):
        jr = self.j.request_organization(self.o)
        self.assertEqual(0,len(self.j.jobrequests_accepted()))
        jr.accepted = True
        jr.save()
        self.assertEqual(1,len(self.j.jobrequests_accepted()))
        self.assertTrue(jr in self.j.jobrequests_accepted())

    #check if pending jobreuqests are returned
    def test_jobrequests_pending(self):
        self.assertEqual(0,len(self.j.jobrequests_pending()))
        jr = self.j.request_organization(self.o)
        self.assertEqual(1,len(self.j.jobrequests_pending()))
        self.assertTrue(jr in self.j.jobrequests_pending())

    #rcheck if declined jobrequests are returned
    def test_jobrequests_declined(self):
        jr = self.j.request_organization(self.o)
        self.assertFalse(jr in self.j.jobrequests_declined())
        jr.declined = True
        jr.save()
        self.assertTrue(jr in self.j.jobrequests_declined())

    ### Interface Tests ###

    #verify job_creation view
    def test_job_creation(self):
        #Login
        login_as(self,self.u_cp.username,'asdf')
        #check logged in as user0
        response = self.client.get(reverse('front_page'))
        self.assertEqual(response.context['user'],self.u_cp)

        #Create a job
        response = self.client.post(reverse('job_creation'),
                             {
                                 'name':'interfacejob',
                                 'client_organization':'foo',
                                 'description':"testjob description",
                                 'deliverable':'foo',
                                 'duedate':'2016-01-01',
                                 'stakeholders':'foo',
                                 'tech_specs':'foo',
                                 'budget':'foo',
                                 'creator':self.u_cp.pk,
                                 'organizations':self.o.pk,
                                 'categories':self.cat.pk
                             }
                             ,follow=True)
        self.assertEqual(response.status_code, 200)

        #check if job exists
        self.assertTrue(Job.objects.filter(name='interfacejob').first())

        j = Job.objects.filter(name='interfacejob').first()

        # verify job was submitted to organization in `organization` field
        self.assertTrue(self.o in j.organizations.all())

        # verify job was submitted to organizations in `categories` field
        self.assertTrue(self.o2 in j.organizations.all())

    #verify job_dash view
    def test_job_dash(self):
        login_as(self,self.u_cp.username,'asdf')
        response = self.client.get(reverse('job_dash',kwargs={'job_id':self.j.id}))
        self.assertTrue(len(response.context['messages']) == 0)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(self.j == response.context['job'])

    #verify jobrequest_dash view
    def test_jobrequest_dash(self):
        jr = self.j2.request_organization(self.o)

        login_as(self,self.u_pu.username,'asdf')
        response = self.client.get(reverse('jobrequest_dash',kwargs={'job_id':self.j2.id,'organization_id':self.o.id}))
        self.assertTrue(self.u_pu.has_perm('view_jobrequest',jr))
        self.assertTrue(len(response.context['messages']) == 0)
        self.assertEqual(jr,response.context['jobrequest'])
        #test accept job
        logout(self)

        login_as(self,self.u_cp.username,'asdf')
        response = self.client.get(reverse('jobrequest_dash',kwargs={'job_id':self.j2.id,'organization_id':self.o.id}))
        self.assertTrue(len(response.context['messages']) == 0)
        self.assertEqual(jr,response.context['jobrequest'])

    def test_jobrequest_accept_decline(self):
        jr = self.j2.request_organization(self.o)
        login_as(self,self.u_pu.username,'asdf')
        #test that a user cannot accept a jobrequest after it has been accepted/rejected
        jr.accept()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"apply"}, follow=True)
        self.assertTrue('error' in list(response.context['messages'])[0].tags)
        jr.decline()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"apply"}, follow=True)
        self.assertTrue('error' in list(response.context['messages'])[0].tags)

        #test that a user cannot reject a jobrequest after it has been accepted/rejected
        jr.accept()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"notInterested"}, follow=True)
        self.assertTrue('error' in list(response.context['messages'])[0].tags)
        jr.decline()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"notInterested"}, follow=True)
        self.assertTrue('error' in list(response.context['messages'])[0].tags)

        #test that a user can accept/reject a jobrequest when it is still pending
        jr.pend()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"apply"}, follow=True)
        self.assertTrue(response.status_code==200)
        jr.pend()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"notInterested"}, follow=True)
        self.assertTrue(response.status_code==200)
        logout(self)

        #test community user cannot accept/decline a jobrequest
        login_as(self,self.u_cp.username,'asdf')
        jr.pend()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"notInterested"}, follow=True)
        self.assertTrue('error' in list(response.context['messages'])[0].tags)
        jr.pend()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"apply"}, follow=True)
        self.assertTrue('error' in list(response.context['messages'])[0].tags)
        logout(self)
    def test_jobrequest_confirm(self):
        jr = self.j2.request_organization(self.o)
        #make sure it fail to confirm as purdue user
        login_as(self,self.u_pu.username,'asdf')
        jr.confirm()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"confirm"}, follow=True)
        self.assertTrue('error' in list(response.context['messages'])[0].tags)
        #self.assertRedirects(response, reverse('organization_dash', kwargs={'organization_id': self.o.id}), status_code=302, target_status_code=200)
        logout(self)

        #check that it works for community user
        login_as(self,self.u_cp.username,'asdf')
        jr.confirmed = False
        jr.save()
        jr.confirm()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"confirm"}, follow=True)
        self.assertTrue(response.status_code==200)

        #check that it does not work to double confirm it
        jr.confirmed = True
        jr.confirm()
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"confirm"}, follow=True)
        self.assertTrue('error' in list(response.context['messages'])[0].tags)
        logout(self)
    def test_comments(self):
        jr = self.j2.request_organization(self.o)
        login_as(self,self.u_pu.username,'asdf')
        form_data = {'text_comment': 'test case'}
        form = CommentCreateForm(data = form_data)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('jobrequest_dash', kwargs = {'job_id':self.j2.id,'organization_id': self.o.id}), {'action':"comment",'text_comment':'test case'})
        self.assertTrue(response.status_code==302)
        self.assertTrue(jr.comment_set.get(text_comment='test case'))
        logout(self)

class OrganizationTestCase(TestCase):
    #django calls this initialization function automatically
    def setUp(self):
        set_up(self)
        #add foobar_purdueuser to org
        self.o.group.user_set.add(self.u_pu)
        #nonmember_user is not a member
        self.u2 = User.objects.create(username='nonmember_user')
        self.u2.set_password('asdf')
        self.u2.save()
        UserProfile.objects.create(user = self.u2, purdueuser = True)

    ### Backend Tests ###

    #check default permissions on newly created Organizations
    def test_permissions(self):
        self.assertTrue(self.u_pu.has_perm('view_organization',self.o))
        self.assertTrue(self.u_pu.has_perm('edit_organization',self.o))
        self.assertFalse(self.u2.has_perm('view_organization',self.o))
        self.assertFalse(self.u2.has_perm('edit_organization',self.o))

    #test jobrequests_pending member function
    def test_jobrequests_pending(self):
        self.j.request_organization(self.o)
        jr = self.j.request_organization(self.o)
        self.assertTrue(jr in self.o.jobrequests_pending())

    #test jobrequests_declined member function
    def test_jobrequests_declined(self):
        jr = self.j.request_organization(self.o)
        jr.declined = True
        jr.save()
        self.assertTrue(jr in self.o.jobrequests_declined())

    #test jobrequests_completed member function
    def test_jobrequests_completed(self):
        jr = self.j.request_organization(self.o)
        self.assertTrue(jr in self.o.jobrequests_pending())
        jr.completed = True
        jr.save()
        self.assertTrue(jr in self.o.jobrequests_completed())

    #test get_admins member function
    def test_get_admins(self):
        self.o.group.user_set.add(self.u_pu)
        assign_perm('is_admin',self.u_pu,self.o)
        self.assertTrue(self.u_pu in self.o.get_admins())

    ### Interface Tests ###

    #test organization_detail.html
    def test_org_detail(self):
        response = self.client.post(reverse('organization_detail', kwargs = {'organization_id': self.o.id}))
        self.assertTrue(response.status_code == 200)
        self.assertEqual(self.o, response.context['organization'])

    #test organization_dash.html
    def test_organization_dash(self):
        login_as(self, self.u_pu.username, 'asdf')
        response = self.client.get(reverse('organization_dash',kwargs={'organization_id':self.o.id}))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(self.o == response.context['organization'])

    #test org creation
    def test_organization_create(self):
        from johnslist.settings import PIC_POPULATE_DIR
        #when user is not logged in
        response = self.client.post(reverse('organization_create'))
        self.assertEqual(response.status_code, 302)

        #after login
        login_as(self, self.u2.username, 'asdf')
        category = self.cat.pk
        #creating the org
        with open(PIC_POPULATE_DIR+'plug.png') as icon:
            response = self.client.post(reverse('organization_create'),
                                        {'name': 'test org',
                                         'email': 'evan@evanw.org',
                                         'description': 'testing org',
                                         'categories': category,
                                         'icon':icon}
                                        )
        self.assertTrue(response.status_code == 302)
        self.assertTrue(Organization.objects.get(name = 'test org'))
        org = Organization.objects.get(name = 'test org')
        response = self.client.get('/organization/{0}'.format(org.id))
        self.assertTrue(response.status_code == 200)

    #changing the organization attributes
    def test_organization_settings(self):
        self.o.group.user_set.add(self.u2) 
        login_as(self, self.u2.username, 'asdf')
        response = self.client.post(reverse('organization_settings',
                                            kwargs = {'organization_id': self.o.pk}),
                                    {'name': 'test org',
                                     'email': 'evan@evanw.org',
                                     'description': 'testing org',
                                     'categories': self.cat.pk,
                                     }
                                    )
        self.assertEqual(response.status_code, 200)
