#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        username = 'crawlers_admin'
        password = 'crawlers_admin'
        user = User.objects.filter(username=username).first()

        if not user:
            user = User.objects.create_user(username=username, password=password)
            user.save()

        print('Username: `{username}` with password: `{password}` created!'.format(username=username, password=password))
