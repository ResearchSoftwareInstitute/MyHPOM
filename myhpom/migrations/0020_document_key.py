# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myhpom', '0019_auto_20180817_1117'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text=b'The non-guessable string that indentifies this DocumentKey.', unique=True, max_length=48)),
                ('expiration', models.DateTimeField(help_text=b'The optional timestamp indicating when this DocumentKey expires.', null=True, blank=True)),
                ('ip', models.CharField(help_text=b'The optional IP address or range to which this DocumentKey is limited', max_length=64, null=True, blank=True, verbose_name=b'IP')),
                ('advancedirective', models.ForeignKey(help_text=b'The AdvanceDirective to which this URL points.', to='myhpom.AdvanceDirective')),
            ],
        ),
    ]
