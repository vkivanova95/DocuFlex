from common.mixins import GroupRequiredMixin, AnnexPermissionMixin, PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect

from loan_requests.choices import RequestStatus
from loan_requests.utils import get_executors
from .forms import AnnexStandardForm, AdditionalConditionFormSet, AnnexDeletionForm, BaseAnnexStartForm
from .models import Request, GeneratedAnnex
from .utils import generate_annex_standard, generate_annex_deletion
from django.contrib import messages
from django.views.generic import ListView
from logs.models import SystemLog
from django.utils.timezone import now


class GenerateAnnexView(LoginRequiredMixin, GroupRequiredMixin, AnnexPermissionMixin, View):
    allowed_groups = ['изпълнител']

    def get(self, request):
        # Стартовата форма с 4-те основни полета
        start_form = BaseAnnexStartForm()
        return render(request, 'annexes/start_annex_form.html', {
            'start_form': start_form
        })

    def post(self, request):
        # 1. обработваме началната форма (с 4 полета)
        if 'step' not in request.POST:
            start_form = BaseAnnexStartForm(request.POST)
            if start_form.is_valid():
                req = get_object_or_404(Request, request_number=start_form.cleaned_data['request_number'])

                # проверки: заявката да е В процес на работа и да е разпределена
                if req.status != RequestStatus.IN_PROGRESS:
                    messages.error(request,
                                   "Анекс може да се генерира само ако заявката е в статус 'В процес на работа'.")
                    return render(request, 'annexes/start_annex_form.html', {
                        'start_form': start_form
                    })

                if not req.maker:
                    messages.error(request, "Заявката не е разпределена за работа към изпълнител. Не може да се генерира анекс.")
                    return render(request, 'annexes/start_annex_form.html', {
                        'start_form': start_form
                    })

                # ако всичко е наред – продължава към втора стъпка
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

            # ако стартовата форма не е валидна
            return render(request, 'annexes/start_annex_form.html', {
                'start_form': start_form
            })

        # 2. пълна форма
        annex_type = request.POST.get('annex_type', 'standard')
        form_class = self.get_form_class(annex_type)
        form = form_class(
            request.POST,
            initial={
                'request_number': request.POST.get('request_number'),
                'annex_number': request.POST.get('annex_number'),
                'annex_date': request.POST.get('annex_date'),
                'city': request.POST.get('city'),
            }
        )
        formset = (
            AdditionalConditionFormSet(request.POST)
            if annex_type == 'standard'
            else None
        )

        if form.is_valid() and (formset is None or formset.is_valid()):
            req = get_object_or_404(Request, request_number=form.cleaned_data['request_number'])

            if annex_type == 'deletion':
                file_path = generate_annex_deletion(form.cleaned_data, req)
            else:
                extra = [f.cleaned_data['text'] for f in formset if f.cleaned_data]
                file_path = generate_annex_standard(form.cleaned_data, req, extra_conditions=extra)

            if file_path.startswith("media/"):
                file_path = file_path.replace("media/", "")

            # Запис в базата
            annex_obj = GeneratedAnnex.objects.create(
                request=req,
                annex_number=form.cleaned_data['annex_number'],
                annex_date=form.cleaned_data['annex_date'],
                file_path=file_path
            )
            req.preparation_date = now()
            req.save()

            download_url = request.build_absolute_uri(annex_obj.file_path.url)

            messages.success(request,
                             f'Анекс №{form.cleaned_data["annex_number"]} към Договор № {req.loan_agreement.contract_number} е успешно генериран. '
                             f'<a href="{download_url}" target="_blank">Изтегли анекса</a>')

            SystemLog.objects.create(
                user=request.user,
                action='generate_annex',
                model_name='GeneratedAnnex',
                object_id=annex_obj.pk,
                timestamp=now(),
                description=f"Генериран анекс №{annex_obj.annex_number} към договор {req.loan_agreement.contract_number}."
            )

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


class AnnexArchiveView(LoginRequiredMixin, GroupRequiredMixin, PaginationMixin, ListView):
    model = GeneratedAnnex
    template_name = 'annexes/annex_archive.html'
    context_object_name = 'annexes'
    allowed_groups = ['бизнес', 'ръководител', 'изпълнител']

    def get_queryset(self):
        queryset = GeneratedAnnex.objects.select_related(
            'request__client', 'request__loan_agreement', 'request__maker').filter(request__status=RequestStatus.IN_PROGRESS)

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
        context['filters'] = {
            'request_number': self.request.GET.get('request_number', ''),
            'client_name': self.request.GET.get('client_name', ''),
            'eik': self.request.GET.get('eik', ''),
            'contract_number': self.request.GET.get('contract_number', ''),
            'maker': self.request.GET.get('maker', ''),
        }

        context['per_page'] = self.request.GET.get('per_page', str(self.paginate_by))
        return context
