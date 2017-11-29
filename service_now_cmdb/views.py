from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from service_now_cmdb.helper import SNCMDBHandler
from .forms import ServiceNowTokenForm


class ServiceNowTokenView(LoginRequiredMixin, View):
    # Change me
    template_name = ''

    def get(self, request):
        handler = SNCMDBHandler(request.user)
        if handler.get_credentials():
            token = handler.token.__str__()
        else:
            token = False

        form = ServiceNowTokenForm(user=request.user)
        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'service_now_token',
            'token': token
        })

    def post(self, request):
        form = ServiceNowTokenForm(user=request.user, data=request.POST)
        if form.is_valid():
            if form.save():
                messages.success(request, "Your ServiceNow token has been added successfully.")
                return redirect('user:service_now_cmdb:service_now_token')
            messages.error(request, "Your ServiceNow token has not been added successfully. Please verify your username and password.")
            return redirect('user:service_now_cmdb:service_now_token')

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'service_now_token',
        })
