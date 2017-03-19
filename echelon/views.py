# Copyright (c) 2011 Dennis Kaarsemaker <dennis@kaarsemaker.net>
# Small piece of middleware to be able to access authentication data from
# everywhere in the django code.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
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

from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from echelon.models import ChangelogEntry
from utils.model_utils import get_page_choices
import json


@user_passes_test(lambda user: user.is_staff)
def changelog(request):
    log = ChangelogEntry.objects.all()
    selected = request.GET.get('content_type', '').strip()
    changes = request.GET.get('changes', '').strip()
    who = request.GET.get('who', '').strip()
    detail = request.GET.get('detail', '').strip()
    if selected:
        log = log.filter(content_type=selected)

    if who:
        log = log.filter(who__username=who)

    if changes:
        log = log.filter(Q(changes__contains=changes) |
                         Q(action=changes) |
                         Q(before_change__contains=changes) |
                         Q(after_change__contains=changes))
    paginator = Paginator(log.order_by('-timestamp'), 15)

    page_n = request.GET.get('p', '1')
    if not page_n.isdigit():
        page_n = '1'
    page_n = int(page_n)

    try:
        page = paginator.page(page_n)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    modelnames = [str('%s.%s' % (m.app_label, m.model)) for m in ContentType.objects.order_by('app_label', 'model')]
    modelnames = json.dumps(modelnames)

    users = [u['username'] for u in User.objects.all().values('username')]
    users = json.dumps(users)
    ctx = RequestContext(request, {
        'models': modelnames,
        'selected': selected,
        'who': who,
        'changes': changes,
        'users': users,
        'detail': detail,

        'page': page,
        'page_pre': page.has_previous(),
        'page_next': page.has_next(),
        'paginator': paginator,
        'page_n': page_n,
        'page_choices': get_page_choices(page_n, paginator.num_pages),
    })
    return render_to_response('echelon/changelog.html', ctx)
