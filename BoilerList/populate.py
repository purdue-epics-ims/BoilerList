#!/usr/bin/env python2

import os
from django.core.management import call_command
from itertools import cycle
from django.utils import timezone
import sys

def populate():
    print 'Populating database...'

    #--------------- Organizations ----------------
    print '  creating Organizations'

    #add Organizations
    g=Group.objects.create(name="Purdue Linux Users Group")
    plug = Organization.objects.create(
        name=g.name,
        group=g,
        description=" Linux is a free computer operating system. it runs on a large variety of computer hardware, and can be used for many purposes including desktop machines, small embedded systems and internet servers. you can find more information about Linux itself on the Linux international website. the Linux documentation project is also a good place to find general information about Linux.",
        phone_number="123-456-7890",
        url="https://purduelug.org",
        available=False)
    plug.icon.save('plug.png', File(open(PIC_POPULATE_DIR+'plug.png')), 'r')

    g=Group.objects.create(name="Engineering Projects in Community Service")
    epics = Organization.objects.create(
        name=g.name,
        group=g,
        description=" Community service agencies face a future in which they must take advantage of technology to improve, coordinate, account for, and deliver the services they provide. they need the help of people with strong technical backgrounds. undergraduate students face a future in which they will need more than solid expertise in their discipline to succeed. they will be expected to work with people of many different backgrounds to identify and achieve goals. they need educational experiences that can help them broaden their skills. the challenge is to bring these two groups together in a mutually beneficial way. in response to this challenge, purdue university has created epics: engineering projects in community service",
        phone_number="123-456-7890",
        url="https://engineering.purdue.edu/EPICS",
        available=True)
    epics.icon.save('epics.png', File(open(PIC_POPULATE_DIR+'epics.png', 'r')))

    g=Group.objects.create(name="Association of Mechanical & Electrical Technologies")
    amet = Organization.objects.create(
        name=g.name,
        group=g,
        description="The association of mechanical and electrical technologists (amet) is an organization that brings science, technology, engineering, and mathematics (stem)-based students together to discuss and work on various extra-curricular projects throughout the school year. the group is meant to help educate students on what it is like to be in an interdisciplinary team and have fun at the same time. past and current projects include the following: gas grand prix, robosumo competitions, high altitude vehicle launches, a robotic assistant for people with limb paralysis, loudspeaker design / construction, and the national rube goldberg competition. along with projects, amet hosts various company sponsored lectures and recruitment efforts for our students.",
        phone_number="123-456-7890",
        url="https://boilerlink.purdue.edu/organization/amet",
        available=False)
    amet.icon.save('amet.png', File(open(PIC_POPULATE_DIR+'amet.png', 'r')))

    #-------------- Users ------------------
    print '  creating Users'

    #create users
    emails = cycle(['evan@evanw.org','malesevic.milos2@gmail.com'])
    for username_prefix, is_purdueuser in zip(("pu", "cp"), (True, False)):
        for num in range(0,5):
            username = username_prefix + str(num)
            newuser = User.objects.create(username=username, email=emails.next())
            newuser.set_password('asdf')
            newuser.save()
            UserProfile.objects.create(user=newuser, purdueuser=is_purdueuser)
    # create superuser
    superuser = User(username='admin', email='evan@evanw.org')
    superuser.set_password('asdf')
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.save()
    UserProfile.objects.create(user=superuser, purdueuser=False)

    #add Users to Organizations
    users = User.objects.all().exclude(username="AnonymousUser")
    for user in users[0:6]:
        if user.userprofile.purdueuser:
            plug.group.user_set.add(user)
            epics.group.user_set.add(user)
            amet.group.user_set.add(user)

    #--------------- Categories --------------------

    #create category groups
    print '  creating CategoryGroups'
    category_groups = ['art','apps','engineering']
    for category_group in category_groups:
        print '    '+category_group
        CategoryGroup.objects.create(name=category_group,description='')

    #create categories
    print '  creating Categories'
    categories=[('video','art'),('computer science','engineering'),('construction','engineering'),('music','art'),('iOS','apps'),('android','apps'),('painting','art'),('linux','engineering'),('web development','art')]
    for category in categories:
        print '    '+category[0]
        Category.objects.create(name=category[0], group=CategoryGroup.objects.get(name=category[1]))

    #tag Organizations with Categories
    plug.categories.add(Category.objects.get(name="computer science"), Category.objects.get(name="linux"))
    epics.categories.add(Category.objects.get(name='construction'))
    epics.categories.add(Category.objects.get(name='web development'))
    amet.categories.add(Category.objects.get(name='construction'))

    #--------------- Jobs --------------------
    print '  creating Jobs'

    #create Jobs
    jobs = ['Planning student success series','Advertising for employment training', 'Install irrigation system', 'Story Collection', 'Finish software']

    community_partners = cycle([user_profile.user for user_profile in UserProfile.objects.filter(purdueuser=False)])
    client_orgs = cycle(["Beacon Academy","Lafayette Adult Resources","Lafayette City Farms", "Bauer Family resources"])
    orgs = cycle(Organization.objects.all())
    categories = cycle(Category.objects.all())

    #create JobRequests
    for job_name in jobs:
        print '    '+job_name
        job = Job.objects.create(name=job_name,
                                description='Description of the job',                
                                deliverable='deliverable',
                                #stakeholders='stakeholders',
                                #additional_information='additional_information',
                                #budget='budget',
                                contact_information='contact_information@gmail.com',
                                duedate=timezone.now(),
                                creator=community_partners.next(),
                                client_organization=client_orgs.next())
        #Make some jobrequests "randomly"
        if job.id % 2 == 0:
            jr = job.request_organization(orgs.next())
            # jr.decline()
        jr = job.request_organization(orgs.next())
        # jr.accept()
        jr = job.request_organization(orgs.next())

        job.categories.add(categories.next())


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'johnslist.settings')
    import django
    django.setup()
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
    call_command('makemigrations', interactive=True)
    call_command('migrate', interactive=True)
    call_command('migrate', 'main', interactive=False)
    from django.core.files import File
    from main.models import *
    from johnslist.settings import PIC_POPULATE_DIR
    from time import sleep

    populate()
