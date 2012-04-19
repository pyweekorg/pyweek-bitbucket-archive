#! /usr/bin/env python

import sys

from django.core.management import setup_environ
from pyweek import settings
setup_environ(settings)

from pyweek.challenge import models

#from django.contrib import auth
#from django.db import connection

try:
    replace_name = sys.argv[1]
    keep_name = sys.argv[2]
except IndexError:
    sys.exit('usage: %s <user to replace> <user to keep>'%sys.argv[0])

try:
    replace_user = models.User.objects.filter(username__exact=replace_name)[0]
except IndexError:
    sys.exit('''"replace" user %r does not exist!
usage: %s <user to replace> <user to keep>'''%(replace_name, sys.argv[0]))
try:
    keep_user = models.User.objects.filter(username__exact=keep_name)[0]
except IndexError:
    sys.exit('''"keep" user %r does not exist!
usage: %s <user to replace> <user to keep>'''%(keep_name, sys.argv[0]))
l = []
for model in (models.Entry, models.Rating, models.DiaryEntry,
        models.DiaryComment, models.File, models.Response):
    for entry in model.objects.filter(user=replace_user):
        l.append(('user', entry))
for entry in models.Entry.objects.filter(users=replace_user):
    l.append(('users', entry))
for entry in models.DiaryEntry.objects.filter(actor=replace_user):
    l.append(('actor', entry))
for entry in models.UserProfile.objects.filter(user=replace_user):
    l.append(('delete', entry))

if not l:
    print 'NOTHING FOUND FOR %r'%replace_user
    sys.exit(0)

print 'Found these entries for %s'%replace_user
for t, o in l:
    print t, o
ok = raw_input('Replace with %s [y/n]? '%keep_user)
if ok == 'y':
    for t, o in l:
        if t == 'user':
            o.user = keep_user
            o.save()
        elif t == 'delete':
            o.delete()
        elif t == 'users':
            o.users.remove(replace_user)
            if keep_user not in o.users.all():
                o.users.add(keep_user)
            o.save()
        elif t == 'actor':
            o.actor = keep_user
            o.save()
        else:
            print 'UNHANDLED', t, o
    replace_user.delete()

