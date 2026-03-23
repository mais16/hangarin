from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Task, SubTask, Note, Category, Priority
from .forms import TaskForm, SubTaskForm, NoteForm, CategoryForm, PriorityForm


# ─── Dashboard ────────────────────────────────────────────────────────────────

def dashboard(request):
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status="Completed").count()
    pending_tasks = Task.objects.filter(status="Pending").count()
    in_progress_tasks = Task.objects.filter(status="In Progress").count()
    tasks_this_year = Task.objects.filter(created_at__year=timezone.now().year).count()

    overdue_tasks = [t for t in Task.objects.exclude(status="Completed") if t.is_overdue]
    recent_tasks = Task.objects.select_related('category', 'priority').order_by('-created_at')[:5]

    # Category breakdown
    category_data = (
        Category.objects.annotate(task_count=Count('tasks'))
        .order_by('-task_count')[:5]
    )

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'tasks_this_year': tasks_this_year,
        'overdue_count': len(overdue_tasks),
        'recent_tasks': recent_tasks,
        'category_data': category_data,
    }
    return render(request, 'tasks/dashboard.html', context)


# ─── Task List ────────────────────────────────────────────────────────────────

def task_list(request):
    tasks = Task.objects.select_related('category', 'priority')

    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority__id=priority_filter)

    category_filter = request.GET.get('category', '')
    if category_filter:
        tasks = tasks.filter(category__id=category_filter)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    sort_map = {
        'title': 'title',
        '-title': '-title',
        'deadline': 'deadline',
        '-deadline': '-deadline',
        'created_at': 'created_at',
        '-created_at': '-created_at',
        'status': 'status',
        '-status': '-status',
    }
    if sort_by in sort_map:
        tasks = tasks.order_by(sort_map[sort_by])
    else:
        tasks = tasks.order_by('-created_at')

    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'sort_by': sort_by,
        'priorities': Priority.objects.all(),
        'categories': Category.objects.all(),
        'total_count': tasks.count(),
    }
    return render(request, 'tasks/task_list.html', context)


# ─── Task Detail ──────────────────────────────────────────────────────────────

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    subtasks = task.subtasks.all()
    notes = task.notes.all().order_by('-created_at')
    subtask_form = SubTaskForm()
    note_form = NoteForm()

    context = {
        'task': task,
        'subtasks': subtasks,
        'notes': notes,
        'subtask_form': subtask_form,
        'note_form': note_form,
        'completed_subtasks': subtasks.filter(status='Completed').count(),
        'total_subtasks': subtasks.count(),
    }
    return render(request, 'tasks/task_detail.html', context)


# ─── Task Create ──────────────────────────────────────────────────────────────

def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


# ─── Task Update ──────────────────────────────────────────────────────────────

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Update', 'task': task})


# ─── Task Delete ──────────────────────────────────────────────────────────────

def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" deleted.')
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


# ─── SubTask CRUD ─────────────────────────────────────────────────────────────

def subtask_create(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == 'POST':
        form = SubTaskForm(request.POST)
        if form.is_valid():
            subtask = form.save(commit=False)
            subtask.parent_task = task
            subtask.save()
            messages.success(request, 'Sub-task added!')
    return redirect('task_detail', pk=task_pk)


def subtask_update(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk)
    if request.method == 'POST':
        form = SubTaskForm(request.POST, instance=subtask)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sub-task updated!')
    return redirect('task_detail', pk=subtask.parent_task.pk)


def subtask_delete(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk)
    task_pk = subtask.parent_task.pk
    if request.method == 'POST':
        subtask.delete()
        messages.success(request, 'Sub-task deleted.')
    return redirect('task_detail', pk=task_pk)


def subtask_toggle(request, pk):
    """Quick toggle subtask status via AJAX or direct POST."""
    subtask = get_object_or_404(SubTask, pk=pk)
    if request.method == 'POST':
        if subtask.status == 'Completed':
            subtask.status = 'Pending'
        else:
            subtask.status = 'Completed'
        subtask.save()
        messages.success(request, 'Sub-task status updated.')
    return redirect('task_detail', pk=subtask.parent_task.pk)


# ─── Note CRUD ────────────────────────────────────────────────────────────────

def note_create(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.task = task
            note.save()
            messages.success(request, 'Note added!')
    return redirect('task_detail', pk=task_pk)


def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    task_pk = note.task.pk
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
    return redirect('task_detail', pk=task_pk)


# ─── Category CRUD ────────────────────────────────────────────────────────────

def category_list(request):
    search_query = request.GET.get('q', '')
    categories = Category.objects.annotate(task_count=Count('tasks'))
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    paginator = Paginator(categories, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'tasks/category_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })


def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f'Category "{cat.name}" created!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'tasks/category_form.html', {'form': form, 'action': 'Create'})


def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'tasks/category_form.html', {'form': form, 'action': 'Update', 'category': category})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
        return redirect('category_list')
    return render(request, 'tasks/category_confirm_delete.html', {'category': category})


# ─── Priority CRUD ────────────────────────────────────────────────────────────

def priority_list(request):
    search_query = request.GET.get('q', '')
    priorities = Priority.objects.annotate(task_count=Count('tasks'))
    if search_query:
        priorities = priorities.filter(name__icontains=search_query)

    paginator = Paginator(priorities, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'tasks/priority_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })


def priority_create(request):
    if request.method == 'POST':
        form = PriorityForm(request.POST)
        if form.is_valid():
            p = form.save()
            messages.success(request, f'Priority "{p.name}" created!')
            return redirect('priority_list')
    else:
        form = PriorityForm()
    return render(request, 'tasks/priority_form.html', {'form': form, 'action': 'Create'})


def priority_update(request, pk):
    priority = get_object_or_404(Priority, pk=pk)
    if request.method == 'POST':
        form = PriorityForm(request.POST, instance=priority)
        if form.is_valid():
            form.save()
            messages.success(request, 'Priority updated!')
            return redirect('priority_list')
    else:
        form = PriorityForm(instance=priority)
    return render(request, 'tasks/priority_form.html', {'form': form, 'action': 'Update', 'priority': priority})


def priority_delete(request, pk):
    priority = get_object_or_404(Priority, pk=pk)
    if request.method == 'POST':
        priority.delete()
        messages.success(request, 'Priority deleted.')
        return redirect('priority_list')
    return render(request, 'tasks/priority_confirm_delete.html', {'priority': priority})
