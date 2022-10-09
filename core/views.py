from django.shortcuts import render, redirect
from . import forms
from django.http import HttpRequest
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models
from bso import data_reader
from django.views import View

# Create your views here.

def landing(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'landing_page.html', context={'form': forms.Form()})

    form = forms.Form(request.POST, request.FILES)
    if form.is_valid():
        obj = form.save(commit=False)
        if request.user.is_authenticated:
            obj.owner = request.user
        obj.save()
        dataset_name = request.FILES['docfile'].name.split(".")[0]
        transactions = data_reader.read_data(f"media/{obj.docfile.name}")
        obj.name = dataset_name
        obj.nbr_transactions = transactions.nbr_transactions
        obj.nbr_items = transactions.nbr_items
        obj.average_nbr_items_per_transaction = transactions.average_nbr_items_per_transaction
        obj.density_index = transactions.density_index
        obj.save()
        return redirect(request.GET.get('next', f'/processing/{obj.id}'))


class DatasetsListView(LoginRequiredMixin, ListView):
    template_name = 'core/datasets_list.html'
    context_object_name = 'datasets'

    def get_queryset(self):
        queryset = models.Document.objects.filter(owner=self.request.user)
        return queryset

class DatasetDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'core/dataset_delete.html'
    queryset = models.Document.objects.all()

    def get_success_url(self):
        return '/myDatasets/'


class RegisterView(View):
    def get(self, request):
        return render(request, 'registration/register.html')

    def post(self, request):
        form = forms.CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login?next=/myDatasets/')
        context = {'form': form, 'not_valid': True}
        print(form.errors)
        return render(request, 'registration/register.html', context=context)
