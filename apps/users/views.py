# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render, render_to_response, redirect
from django.utils.translation import activate

from .forms import UserCreationForm


def auth_login(request):
    #activate(lang)
    msg = []
    if request.method == 'POST':
        # try log in user
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/login/')
            else:
                # Return a 'disabled account' error message
                msg.append("Account doesn't exist or disabled")
                return HttpResponse('disabled account?')
        else:
            # Return an 'invalid login' error message.
            return HttpResponse('O_o, invalid login')


    else:
        #return render_to_response('users/login.html')
        template = loader.get_template('users/login.html')
        context = RequestContext(request,
            { 'errors':msg }
        )
        return HttpResponse(template.render(context))

def auth_logout(request):
    logout(request)
    return redirect('/login/')
    # Redirect to a success page.

# new user registration
def auth_register(request):
    """ User sign up form """
    if request.method == 'POST':
        data = request.POST.copy() # so we can manipulate data

        # random username
        form = UserCreationForm(data)

        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect('/login/')
    else:
        form = UserCreationForm()

    return render_to_response('users/register.html', {'form':form},
                              context_instance=RequestContext(request))
