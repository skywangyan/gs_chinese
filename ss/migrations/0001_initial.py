# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-05 05:00
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account_money',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField(default=0.0)),
                ('raise_vote_income', models.FloatField(default=0.0)),
                ('answer_vote_income', models.FloatField(default=0.0)),
                ('red_packet_balance', models.FloatField(default=0.0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Answer_choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_description', models.CharField(max_length=10000)),
                ('chosen_times', models.IntegerField(default=0)),
                ('win', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_title', models.CharField(max_length=1000)),
                ('question_description', models.CharField(max_length=10000)),
                ('question_images', models.ImageField(blank=True, null=True, upload_to='upload')),
                ('question_videos', models.CharField(blank=True, max_length=1000, null=True)),
                ('choice_number', models.IntegerField(default=0)),
                ('price_per_ticket', models.FloatField()),
                ('time_ticket_switch', models.IntegerField(default=1)),
                ('whole_tickets', models.IntegerField(default=-1)),
                ('remaining_tickets', models.IntegerField(default=0)),
                ('tickets_sold', models.IntegerField(default=0)),
                ('starting_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('whole_time', models.IntegerField(default=-1)),
                ('time_out', models.BooleanField(default=False)),
                ('ratio', models.FloatField(default=0.0)),
                ('time_ticket_switch_title', models.CharField(max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_title', models.CharField(max_length=100)),
                ('subject_logo', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_tickets', models.IntegerField(default=0)),
                ('vote_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('choice', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ss.Answer_choice')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ss.Question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ss.Subject'),
        ),
        migrations.AddField(
            model_name='question',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='favorite',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ss.Question'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='answer_choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ss.Question'),
        ),
    ]
