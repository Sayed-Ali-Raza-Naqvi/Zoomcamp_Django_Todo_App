from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Todo
from django import forms


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date', 'is_completed']


def home(request):
    todos = Todo.objects.order_by('-created_at')
    return render(request, 'todo/home.html', {'todos': todos})


def create_todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TodoForm()
    return render(request, 'todo/create.html', {'form': form})


def edit_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TodoForm(instance=todo)

    return render(request, 'todo/edit.html', {'form': form, 'todo': todo})



def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        todo.delete()
        return redirect('home')
    return render(request, 'todo/delete_confirm.html', {'todo': todo})


def toggle_complete(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.is_completed = not todo.is_completed
    todo.save()
    return redirect('home')