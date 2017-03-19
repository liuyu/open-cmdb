# Copyright (c) 2009-2011 Dennis Kaarsemaker <dennis@kaarsemaker.net>
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

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import SubfieldBase
from django.db.models.fields import TextField
from django.db.models.fields.related import ForeignKey, ManyToOneRel
from echelon.middleware import EchelonMiddleware
import json


if 'echelon' not in settings.INSTALLED_APPS:
    raise ValueError("Echelon middleware is not enabled")


# Register fields with south, if installed
if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^echelon\.fields\.CurrentUserField"])
    add_introspection_rules([], ["^echelon\.fields\.ChangelogField"])


class CurrentUserField(ForeignKey):
    def __init__(self, to_field=None, rel_class=ManyToOneRel, **kwargs):
        self.add_only = kwargs.pop('add_only', False)
        kwargs.update({
          'editable': False,
          'null': True,
          'rel_class': rel_class,
          'to': User,
          'to_field': to_field,
        })
        super(CurrentUserField, self).__init__(**kwargs)

    def pre_save(self, model_instance, add):
        if add or not self.add_only:
            user = EchelonMiddleware.get_user()
            if user and user.is_authenticated():
                # Do something for authenticated users.
                setattr(model_instance, self.attname, user.pk)
                return user.pk

        return super(CurrentUserField, self).pre_save(model_instance, add)


class ChangelogField(TextField):
    __metaclass__ = SubfieldBase
    marker = '__Echelon_ChangelogField'

    def to_python(self, value):
        if isinstance(value, basestring):
            if value.startswith(self.marker):
                return json.loads(str(value[len(self.marker):]))
        return value

    def get_prep_value(self, value):
        return self.marker + json.dumps(value, )
