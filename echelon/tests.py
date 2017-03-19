# Copyright (c) 2011 Dennis Kaarsemaker <dennis@kaarsemaker.net>
#               2011 Atamert Olcgen <muhuk@muhuk.com>
# Small piece of middleware to be able to access authentication data from
# everywhere in the django code.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#     3. Neither the name of Django nor the names of its contributors may be used
#        to endorse or promote products derived from this software without
#        specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from django.conf.urls import patterns
from django.db import models
from django.http import HttpResponse
from django.test import TestCase
from django.contrib.auth.models import User
from echelon.fields import CurrentUserField
from echelon.middleware import EchelonMiddleware
from echelon.models import ChangelogEntry


class TestModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    creator = CurrentUserField(add_only=True,
                               blank=True,
                               null=True,
                               related_name="tests_created")

    echelon_log_changes = False


class TestModel2(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.IntegerField()


def test_view(request):
    user = EchelonMiddleware.get_user()
    return HttpResponse(user and user.username or u"")


class EchelonTestCase(TestCase):
    urls = patterns('',
        (r"^test-view/", test_view, {}, "test-view"),
    )

    def setUp(self):
        self.user = User.objects.create_user("test", "test@example.com", "test")

    def test_echelon_middleware(self):
        response = self.client.get("/test-view/")
        self.assertEqual(response.content, u"")
        self.client.login(username="test", password="test")
        response = self.client.get("/test-view/")
        self.assertEqual(response.content, u"test")

    def test_current_user_field(self):
        user = User.objects.get(username="test")
        EchelonMiddleware.set_user(user)
        TestModel.objects.create(name="TEST")
        EchelonMiddleware.del_user()
        test_instance = TestModel.objects.get(name="TEST")
        self.assertEqual(test_instance.creator, user)

    def test_current_user_field_with_no_active_user(self):
        EchelonMiddleware.del_user()
        TestModel.objects.create(name="TEST")
        test_instance = TestModel.objects.get(name="TEST")
        self.assertEqual(test_instance.creator, None)

    def test_changelog(self):
        self.assertEqual(ChangelogEntry.objects.for_instance(self.user).count(), 1)
        self.assertEqual(ChangelogEntry.objects.for_model(self.user).count(), 1)

    def test_no_logging(self):
        TestModel(name="dont_log_me").save()
        self.assertEqual(ChangelogEntry.objects.for_model(TestModel).count(), 0)

    def test_changelog_actions(self):
        obj = TestModel2(name='log_me', value=1)
        obj.save()
        obj.value=2
        obj.save()
        EchelonMiddleware.set_user('test')
        TestModel2.objects.all().update(value=3)
        TestModel2.objects.get(pk=obj.pk).delete()

        cl = ChangelogEntry.objects.for_instance(obj).order_by('id')
        self.assertEqual(cl.count(), 4)
        self.assertEqual(list(cl.values_list('action', flat=True)), [u'add', u'change', u'change', u'delete'])
        self.assertEqual(cl[0].changes, {'id': (None, '1'), 'value': (None, u'1'), 'name': (None, u'log_me')})
        self.assertEqual(cl[1].changes, {'value': (u'1', u'2')})
        self.assertEqual(cl[2].changes, {'value': (u'2', u'3')})
        self.assertEqual(cl[3].changes, {'id': (u'1', None), 'value': (u'3', None), 'name': (u'log_me', None)})
        self.assertEqual(cl[0].who, None)
        self.assertEqual(cl[2].who.id, 1)
