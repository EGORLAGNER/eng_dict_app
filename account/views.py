from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserEditForm
from django.contrib import messages



@login_required()
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # создать новый объект пользователя,
            # но пока не сохранять его
            new_user = user_form.save(commit=False)
            # установить выбранный пароль
            new_user.set_password(user_form.cleaned_data['password'])
            # сохранить объект User
            new_user.save()
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required()
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance=request.user,
            data=request.POST
        )
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Профиль успешно изменен')
        else:
            messages.error(request, 'Ошибка изменения профиля')

    else:
        user_form = UserEditForm(
            instance=request.user,  # экземпляр(instance) предаётся в форму, чтобы наполнить её данными
        )

    return render(request,
                  'account/edit.html',
                  {'user_form': user_form}
                  )
