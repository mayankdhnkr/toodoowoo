from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    return render(request, 'todo/home.html')

def usersignup(request):
    if request.method == 'GET':
        return render(request, 'todo/usersignup.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user=User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodoos')
            except IntegrityError:
                return render(request, 'todo/usersignup.html', {'form':UserCreationForm() , 'error':'Username already taken'})

        else:
            return render(request, 'todo/usersignup.html', {'form':UserCreationForm() , 'error':'Passwords did not match'})          

def userlogin(request):
    if request.method == 'GET':
        return render(request, 'todo/userlogin.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/userlogin.html', {'form':AuthenticationForm(), 'error':"Username and password did not match"})
        else:
            login(request, user)
            return redirect('currenttodoos')

@login_required
def userlogout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def createtodoos(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodoos.html', {'form':TodoForm()})
    else:
        try:
            form=TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodoos')
        except ValueError:
            return render(request, 'todo/createtodoos.html', {'form':TodoForm(), 'error':'Bad data passed in. Try again.'})

@login_required
def currenttodoos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)  
    return render(request, 'todo/currenttodoos.html', {'todos':todos})

@login_required
def viewtodoo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo) 
        return render(request, 'todo/viewtodoo.html', {'todo':todo, 'form':form})
    else:
        try:
            form=TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodoos')
        except ValueError:
            return render(request, 'todo/viewtodoo.html', {'todo':todo, 'form':form, 'error':'Bad info'})

@login_required
def completetodoo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodoos')

@login_required
def deletetodoo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodoos')

@login_required
def completedtodoos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodoos.html', {'todos':todos})