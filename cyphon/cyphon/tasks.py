# -*- coding: utf-8 -*-
# Copyright 2017 Dunbar Security Solutions, Inc.
#
# This file is part of Cyphon Engine.
#
# Cyphon Engine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Cyphon Engine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cyphon Engine. If not, see <http://www.gnu.org/licenses/>.
"""
[`source`_]

Cyphon Celery tasks.

.. _source: ../_modules/cyphon/tasks.html

"""

# third party
from django.apps import apps
from django.conf import settings
from django.db import close_old_connections

# local
from aggregator.filters.services import execute_filter_queries
from cyphon.celeryapp import app


@app.task(name='celery.ping')
def ping():
    """Simple task that just returns 'pong'."""
    return 'pong'


@app.task(name='tasks.get_new_mail')
def get_new_mail():
    """
    Checks mail for all Mailboxes.
    """
    mailbox_model = apps.get_model(app_label='django_mailbox',
                                   model_name='mailbox')
    mailboxes = mailbox_model.objects.all()

    for mailbox in mailboxes:
        mailbox.get_new_mail()

    close_old_connections()


@app.task(name='tasks.run_health_check')
def run_health_check():
    """
    Gathers all active Monitors and updates their status.
    """
    monitor_model = apps.get_model(app_label='monitors', model_name='monitor')
    monitors = monitor_model.objects.find_enabled()

    for monitor in monitors:
        monitor.update_status()

    close_old_connections()


@app.task(name='tasks.run_bkgd_search')
def run_bkgd_search():
    """
    Runs background queries.
    """
    execute_filter_queries()
    close_old_connections()


@app.task(name='tasks.start_supplylink')
def start_supplylink(data, supplylink_id, supplyorder_id):
    """

    """
    supplylink_model = apps.get_model(app_label='supplychains',
                                      model_name='supplylink')
    supplylink = supplylink_model.objects.get(pk=supplylink_id)

    supplyorder_model = apps.get_model(app_label='supplyorders',
                                       model_name='supplyorder')
    supplyorder = supplyorder_model.objects.get(pk=supplyorder_id)

    result = supplylink.process(data, supplyorder)
    close_old_connections()
    return result
