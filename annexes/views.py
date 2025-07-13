from django.conf import settings
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect

from loan_requests.utils import get_executors
from .forms import AnnexStandardForm, AdditionalConditionFormSet, AnnexDeletionForm, BaseAnnexStartForm
from .models import Request, GeneratedAnnex
from .utils import generate_annex_standard, generate_annex_deletion
from django.contrib import messages
from django.views.generic import ListView


class GenerateAnnexView(View):
    def get(self, request):
        # Стартовата форма с 4-те основни полета
        start_form = BaseAnnexStartForm()
        return render(request, 'annexes/start_annex_form.html', {
            'start_form': start_form
        })

    def post(self, request):
        # 1. Ако няма 'step' -> обработваме началната форма (с 4 полета)
        if 'step' not in request.POST:
            start_form = BaseAnnexStartForm(request.POST)
            if start_form.is_valid():
                req = get_object_or_404(Request, request_number=start_form.cleaned_data['request_number'])
                annex_type = req.document_type

                form_class = self.get_form_class(annex_type)
                form = form_class(initial=start_form.cleaned_data)

                formset = AdditionalConditionFormSet() if annex_type == 'standard' else None

                return render(request, 'annexes/complete_annex_form.html', {
                    'form': form,
                    'formset': formset,
                    'annex_type': annex_type,
                    'step': 'complete',
                })

            # невалидна стартова форма
            return render(request, 'annexes/start_annex_form.html', {
                'start_form': start_form
            })

        # 2. Втората стъпка – пълна форма
        annex_type = request.POST.get('annex_type', 'standard')
        form_class = self.get_form_class(annex_type)
        form = form_class(request.POST)
        formset = AdditionalConditionFormSet(request.POST) if annex_type == 'standard' else None

        if form.is_valid() and (formset is None or formset.is_valid()):
            req = get_object_or_404(Request, request_number=form.cleaned_data['request_number'])

            if annex_type == 'deletion':
                file_path = generate_annex_deletion(form.cleaned_data, req)
            else:
                extra = [f.cleaned_data['text'] for f in formset if f.cleaned_data]
                file_path = generate_annex_standard(form.cleaned_data, req, extra_conditions=extra)

            # Увери се, че file_path няма media/
            if file_path.startswith("media/"):
                file_path = file_path.replace("media/", "")

            # Запис в базата
            annex_obj = GeneratedAnnex.objects.create(
                request=req,
                annex_number=form.cleaned_data['annex_number'],
                annex_date=form.cleaned_data['annex_date'],
                file_path=file_path
            )

            download_url = request.build_absolute_uri(annex_obj.file_path.url)

            messages.success(request,
                             f'Анекс №{form.cleaned_data["annex_number"]} към Договор № {req.loan_agreement.contract_number} е успешно генериран. '
                             f'<a href="{download_url}" target="_blank">Изтегли анекса</a>')

            return redirect('home')

        # при грешка – връщаме обратно формата
        messages.error(request, "Формата съдържа грешки. Моля, проверете въведените данни.")
        return render(request, 'annexes/complete_annex_form.html', {
            'form': form,
            'formset': formset,
            'annex_type': annex_type,
            'step': 'complete',
        })

    def get_form_class(self, annex_type):
        return AnnexDeletionForm if annex_type == 'deletion' else AnnexStandardForm


class AnnexArchiveView(ListView):
    model = GeneratedAnnex
    template_name = 'annexes/annex_archive.html'
    context_object_name = 'annexes'
    paginate_by = 20

    def get_queryset(self):
        queryset = GeneratedAnnex.objects.select_related(
            'request__client', 'request__loan_agreement', 'request__maker'
        )

        request_number = self.request.GET.get('request_number')
        eik = self.request.GET.get('eik')
        contract_number = self.request.GET.get('contract_number')

        if request_number:
            queryset = queryset.filter(request__request_number__icontains=request_number)

        if eik:
            queryset = queryset.filter(request__client__eik__icontains=eik)

        if contract_number:
            queryset = queryset.filter(request__loan_agreement__contract_number__icontains=contract_number)


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['makers'] = get_executors()
        # Подаваме стойностите от филтъра
        context['filters'] = {
            'request_number': self.request.GET.get('request_number', ''),
            'client_name': self.request.GET.get('client_name', ''),
            'eik': self.request.GET.get('eik', ''),
            'contract_number': self.request.GET.get('contract_number', ''),
            'maker': self.request.GET.get('maker', ''),
        }

        context['per_page'] = self.get_paginate_by(self.get_queryset())
        return context