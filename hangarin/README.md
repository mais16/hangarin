# Hangarin — To-Do Manager

A Django-based To-Do web application with full CRUD, dashboard, search, filtering, sorting, and pagination.

---

## 📁 Project Structure

```
hangarin/
├── manage.py
├── requirements.txt
├── todoproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── tasks/
    ├── __init__.py
    ├── admin.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    ├── management/
    │   └── commands/
    │       └── seed_data.py
    └── templates/
        └── tasks/
            ├── base.html
            ├── dashboard.html
            ├── task_list.html
            ├── task_detail.html
            ├── task_form.html
            ├── task_confirm_delete.html
            ├── category_list.html
            ├── category_form.html
            ├── category_confirm_delete.html
            ├── priority_list.html
            ├── priority_form.html
            └── priority_confirm_delete.html
```

---

## 🚀 Local Setup

### 1. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a superuser (for Admin Panel)
```bash
python manage.py createsuperuser
```

### 5. Seed the database with fake data
```bash
python manage.py seed_data
```

### 6. Run the development server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/
Admin: http://127.0.0.1:8000/admin/

---

## 🌐 Deploying to PythonAnywhere

### 1. Sign up / Log in at https://www.pythonanywhere.com

### 2. Open a Bash console and clone or upload your project
```bash
# If using git:
git clone https://github.com/YOUR_USERNAME/hangarin.git

# Or upload via the Files tab
```

### 3. Create a virtual environment on PythonAnywhere
```bash
mkvirtualenv hangarin-env --python=python3.11
pip install -r hangarin/requirements.txt
```

### 4. Set up the Web App
- Go to the **Web** tab → **Add a new web app**
- Choose **Manual configuration** → **Python 3.11**
- Set the **Source code** directory to: `/home/yourusername/hangarin`
- Set the **Working directory** to: `/home/yourusername/hangarin`

### 5. Configure WSGI file
Edit the WSGI configuration file (linked on the Web tab):
```python
import os
import sys

path = '/home/yourusername/hangarin'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'todoproject.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 6. Update settings.py for production
In `todoproject/settings.py`, update:
```python
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
DEBUG = False
```

### 7. Configure Static Files
On the **Web** tab → **Static files**:
- URL: `/static/`
- Directory: `/home/yourusername/hangarin/staticfiles`

Then run:
```bash
python manage.py collectstatic
```

### 8. Run migrations on PythonAnywhere
```bash
cd hangarin
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
```

### 9. Reload the web app
Click the green **Reload** button on the Web tab.

---

## ✨ Features

| Feature | Details |
|---|---|
| Dashboard | Live stats: total, completed, pending, this year, overdue |
| Task CRUD | Create, Read, Update, Delete tasks |
| Sub-Tasks | Add, toggle, delete per-task sub-tasks with progress bar |
| Notes | Add/delete notes per task |
| Category CRUD | Full management with task count |
| Priority CRUD | Full management with task count |
| Search | Search by title, description, or category |
| Filter | Filter by status, priority, category |
| Sort | Sort by title, deadline, created_at, status |
| Pagination | 10 items per page across all list views |
| Admin Panel | Fully configured with search, filters, custom displays |

---

## 🗄️ Models

- **BaseModel** — Abstract model with `created_at`, `updated_at`
- **Priority** — name (High, Medium, Low, Critical, Optional)
- **Category** — name (Work, School, Personal, Finance, Projects)
- **Task** — title, description, deadline, status (choices), category FK, priority FK
- **Note** — content, task FK
- **SubTask** — title, status (choices), parent_task FK

---

## 🔗 URL Routes

| URL | Name | View |
|---|---|---|
| `/` | `dashboard` | Dashboard overview |
| `/tasks/` | `task_list` | Task list with search/sort/filter |
| `/tasks/create/` | `task_create` | Create task |
| `/tasks/<pk>/` | `task_detail` | View task, subtasks, notes |
| `/tasks/<pk>/edit/` | `task_update` | Edit task |
| `/tasks/<pk>/delete/` | `task_delete` | Delete task |
| `/categories/` | `category_list` | Category list |
| `/priorities/` | `priority_list` | Priority list |
| `/admin/` | — | Django admin panel |
