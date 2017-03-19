# Copyright (c) 2011 Dennis Kaarsemaker <dennis@kaarsemaker.net>
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

from django.conf import settings
from django.db import models
#from django.contrib.contenttypes.models import ContentType
from echelon.fields import CurrentUserField, ChangelogField
from django.utils.translation import ugettext_lazy as _

class ChangelogManager(models.Manager):
    def for_model(self, model):
        #return self.filter(content_type=ContentType.objects.get_for_model(model))
        return self.filter(content_type=model._meta)

    def for_instance(self, instance):
        #return self.filter(content_type=ContentType.objects.get_for_model(instance), object_id=instance.pk)
        return self.filter(content_type=instance.__class__._meta, object_id=instance.pk)


class ChangelogEntry(models.Model):
    content_type = models.CharField(_('content type'), max_length=255, db_index=True)
    #content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField("ID")
    object_str = models.CharField("Object", max_length=100)
    action = models.CharField("Action", choices=(('add','Add'),('change','Change'),('delete','Delete')), max_length=6)
    timestamp = models.DateTimeField("Timestamp", auto_now=True)
    who = CurrentUserField(add_only=True)
    changes = ChangelogField("Changes")
    before_change = ChangelogField("Before Change")
    after_change = ChangelogField("After Change")

    class Meta:
        verbose_name_plural = 'changelog entries'

    # Prevent recursive logging
    echelon_log_changes = False
    objects = ChangelogManager()

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance:
            model = instance.__class__
            # print unicode(instance)
            # print instance.pk, instance.id
            # print model._meta, type(model._meta), dir(model._meta)

            kwargs.update({
                'content_type': model._meta,   #ContentType.objects.get_for_model(instance),
                'object_id': instance.pk or 0, # Don't use None
                'object_str': instance.__unicode__()[:80],
            })

            fields = [x.name for x, _ in model._meta.get_fields_with_model() if not (x.name.endswith('_ptr_id') or x.name.endswith('_ptr'))]

            if not instance.pk:
                kwargs.update({
                    'changes': dict([(x, (None, unicode(getattr(instance, x)))) for x in fields]),
                    'action': 'add',
                    'before_change': dict([(x, None) for x in fields]),
                    'after_change': dict([(x, unicode(getattr(instance, x))) for x in fields]),
                })
            elif kwargs.get('changes',None):
                kwargs.update({
                    'changes': dict([(x, (unicode(getattr(instance, x)), unicode(kwargs['changes'][x])))
                                     for x in kwargs['changes']]),
                    'action': 'change'
                })
            else:
                old = model.objects.get(pk=instance.pk)
                if kwargs.get('action',None) == 'delete':
                    kwargs['changes'] = dict([(x, (unicode(getattr(old, x)), None)) for x in fields])
                else:
                    kwargs.update({
                        'changes': dict([(x, (unicode(getattr(old, x)), unicode(getattr(instance, x))))
                                        for x in fields if getattr(instance, x) != getattr(old, x)]),
                        'action': 'change',
                        'before_change': dict([(x, unicode(getattr(old, x))) for x in fields]),
                        'after_change' : dict([(x, unicode(getattr(instance, x))) for x in fields]),
                    })
        return super(ChangelogEntry, self).__init__(*args, **kwargs)

# Define the signal handlers to automatically save changelogs
def handle_save(sender, **kwargs):
    if (sender._meta.app_label, sender._meta.object_name) in blacklist:
        return

    if getattr(sender, 'echelon_log_changes', True):
        cl = ChangelogEntry(instance=kwargs['instance'])
        if not kwargs['instance'].id:
            kwargs['instance']._cl = cl
        else:
            cl.save()

def handle_post_save(sender, **kwargs):
    cl = getattr(kwargs['instance'], '_cl', None)
    if cl:
        cl.object_id = kwargs['instance'].id
        cl.changes[sender._meta.pk.get_attname()] = (None, str(kwargs['instance'].id))
        cl.save()

def handle_update(sender, **kwargs):
    if (sender._meta.app_label, sender._meta.object_name) in blacklist:
        return
    if getattr(sender, 'echelon_log_changes', True):
        for instance in kwargs['queryset']:
            ChangelogEntry(instance=instance, changes=kwargs['updates']).save()

def handle_delete(sender, **kwargs):
    if (sender._meta.app_label, sender._meta.object_name) in blacklist:
        return
    if getattr(sender, 'echelon_log_changes', True):
        ChangelogEntry(instance=kwargs['instance'], action='delete').save()

# Monkeypatch in pre/post update signals that django does not provide
import django.db.models.signals as signals
import django.db.models.query as query_
signals.pre_update = signals.Signal(providing_args=["queryset","updates"])
signals.post_update = signals.Signal(providing_args=["queryset","updates"])

orig_update = query_.QuerySet.update
def update(self, **kwargs):
    signals.pre_update.send(sender=self.model, queryset=self, updates=kwargs)
    rows = orig_update(self, **kwargs)
    signals.post_update.send(sender=self.model, queryset=self, updates=kwargs)
    return rows
update.alters_data = True
query_.QuerySet.update = update

# And use them for our changelogs
signals.pre_save.connect(handle_save)
signals.post_save.connect(handle_post_save)
signals.pre_update.connect(handle_update)
signals.pre_delete.connect(handle_delete)

blacklist = (
    # Causes infinite recursion
    ('contenttypes', 'ContentType'),
    # Not useful to save
    ('sessions', 'Session'),
    # Admin sideeffects
    ('auth', 'Message'),
    ('admin', 'LogEntry'),
) + getattr(settings, 'ECHELON_LOGGING_BLACKLIST', tuple())
