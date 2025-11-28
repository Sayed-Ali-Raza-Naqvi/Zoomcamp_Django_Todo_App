from django.test import TestCase
from django.urls import reverse
from .models import Todo
from datetime import date

class TodoModelTest(TestCase):
    def test_str(self):
        t = Todo.objects.create(title='Test Todo')
        self.assertEqual(str(t), 'Test Todo')

    def test_default_is_completed(self):
        t = Todo.objects.create(title='Incomplete')
        self.assertFalse(t.is_completed)

class TodoViewsTest(TestCase):
    def setUp(self):
        self.todo = Todo.objects.create(
            title='Sample Todo',
            description='Desc',
            due_date=date(2030, 1, 1)
        )

    def test_home_page_status_and_content(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.todo.title)

    def test_create_todo_valid(self):
        resp = self.client.post(reverse('create_todo'), {
            'title': 'New Todo',
            'description': 'Description',
            'due_date': '2030-02-02',
            'is_completed': False,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())

    def test_create_todo_invalid(self):
        resp = self.client.post(reverse('create_todo'), {
            'title': '',  # missing title
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'This field is required')
        self.assertEqual(Todo.objects.count(), 1)  # no new todo created

    def test_edit_todo_valid(self):
        url = reverse('edit_todo', args=[self.todo.id])
        resp = self.client.post(url, {
            'title': 'Edited Todo',
            'description': 'Updated',
            'due_date': '2030-03-03',
            'is_completed': True,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Edited Todo')
        self.assertTrue(self.todo.is_completed)

    def test_edit_todo_invalid(self):
        url = reverse('edit_todo', args=[self.todo.id])
        resp = self.client.post(url, {
            'title': '',  # invalid
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'This field is required')

    def test_delete_todo_post(self):
        url = reverse('delete_todo', args=[self.todo.id])
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Todo.objects.filter(id=self.todo.id).exists())

    def test_delete_todo_get_shows_confirmation(self):
        url = reverse('delete_todo', args=[self.todo.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Are you sure you want to delete')

    def test_toggle_complete(self):
        url = reverse('toggle_complete', args=[self.todo.id])
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_completed)

    def test_nonexistent_todo_edit_404(self):
        url = reverse('edit_todo', args=[999])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_nonexistent_todo_delete_404(self):
        url = reverse('delete_todo', args=[999])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)
