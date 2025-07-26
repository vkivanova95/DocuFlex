from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from .forms import UserCreateForm, UserUpdateForm, PasswordResetForm
from django.views.generic import TemplateView
from common.mixins import GroupRequiredMixin, PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


def home_redirect_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('users:login')


User = get_user_model()

# проверка за служебна парола
class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        if self.request.user.must_change_password:
            return reverse_lazy('users:force-password-change')
        return reverse_lazy('home')


# смяна служебна парола
class ForcePasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'users/force_password_change.html'
    form_class = PasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        user.must_change_password = False
        user.save()
        update_session_auth_hash(self.request, user)
        return redirect('home')


class UserDashboardView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'users/user-dashboard.html'
    allowed_groups = ['ръководител']

    def test_func(self):
        return (
                self.request.user.is_superuser or
                self.request.user.groups.filter(name__in=['ръководител', 'admin']).exists()
        )


class UserCreateView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ['ръководител']

    def get(self, request):
        form = UserCreateForm()
        return render(request, 'users/create_user.html', {'form': form})

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.must_change_password = True
            user.save()
            group = form.cleaned_data['group']
            user.groups.add(group)
            return redirect('users:user-list')
        return render(request, 'users/create_user.html', {'form': form})


class UserListView(LoginRequiredMixin, GroupRequiredMixin, PaginationMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    allowed_groups = ['ръководител']

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        qs = super().get_queryset().prefetch_related('groups')

        if query:
            qs = qs.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(groups__name__icontains=query)
            ).distinct()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class UserEditView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ['ръководител']

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserUpdateForm(instance=user)
        password_form = PasswordResetForm()
        return render(request, 'users/edit_user.html',
                      {'form': form, 'password_form': password_form, 'user_obj': user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserUpdateForm(request.POST, instance=user)
        password_form = PasswordResetForm(request.POST)

        if 'save_user' in request.POST and form.is_valid():
            group = form.cleaned_data['group']
            user = form.save()
            user.groups.clear()
            user.groups.add(group)
            return redirect('users:user-list')

        elif 'reset_password' in request.POST and password_form.is_valid():
            new_password = password_form.cleaned_data['new_password']
            user.set_password(new_password)
            user.must_change_password = True
            user.save()
            return redirect('users:user-list')

        return render(request, 'users/edit_user.html', {
            'form': form,
            'password_form': password_form,
            'user_obj': user
        })