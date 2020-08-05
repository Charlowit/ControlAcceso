from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.conf import settings



