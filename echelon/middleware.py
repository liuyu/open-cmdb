# Copyright (c) 2009-2011 Dennis Kaarsemaker <dennis@kaarsemaker.net>
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

import thread
from django.contrib.auth.models import User

class EchelonMiddleware(object):
    """Always have access to the current user"""
    __users = {}

    def process_request(self, request):
        """Store user info"""
        self.__class__.set_user(request.user)
    def process_response(self, request, response):
        """Delete user info"""
        self.__class__.del_user()
        return response
    def process_exception(self, request, exception):
        """Delete user info"""
        self.__class__.del_user()

    @classmethod
    def get_user(cls, default=None):
        """Retrieve user info"""
        return cls.__users.get(thread.get_ident(), default)

    @classmethod
    def set_user(cls, user):
        """Store user info"""
        if isinstance(user, basestring):
            user = User.objects.get(username=user)
        cls.__users[thread.get_ident()] = user

    @classmethod
    def del_user(cls):
        """Delete user info"""
        cls.__users.pop(thread.get_ident(), None)
