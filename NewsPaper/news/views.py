from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.views.generic.edit import FormMixin
from django.core.paginator import Paginator  # импортируем класс, позволяющий удобно осуществлять постраничный вывод
# выводить список объектов из БД
from .models import *
from .filters import PostFilter
from .forms import PostForm, CommentForm  # импортируем нашу форму
from datetime import datetime
from django.views import View  # импортируем простую вьюшку

# =============== D5 Авторизация ==============================
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
# ==============================================================
# ================ D6 Рассылка на почту ========================
from django.core.mail import send_mail

from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
# ======================================================
# ============ D6.4 Сигналы ==========================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver  # импортируем нужный декоратор
from django.core.mail import mail_managers, mail_admins


# Create your views here.
class NewsList(ListView):
    model = Post
    template_name = 'news_list.html'
    context_object_name = 'news'
    ordering = ['-dateCreation']
    paginate_by = 10
    form_class = PostForm

    def get_filter(self):
        return PostFilter(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, *args, **kwargs):
        return {
            **super().get_context_data(*args, **kwargs),
            'filter': self.get_filter(),
            'form': self.form_class,
            'all_post': Post.objects.all(),
            'time_now': datetime.utcnow(),
            'is_not_authors': not self.request.user.groups.filter(name='authors').exists(),
            'all_category': Category.objects.filter(),
        }

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)


# дженерик для получения деталей новости
class NewsDetailView(LoginRequiredMixin, PermissionRequiredMixin, FormMixin, DetailView):
    template_name = 'news_detail.html'
    queryset = Post.objects.all()
    context_object_name = 'new'
    permission_required = 'news.add_post'
    form_class = CommentForm

    def get_context_data(self, *args, **kwargs):
        context = super(NewsDetailView, self).get_context_data(**kwargs)
        try:
            context['CP'] = Comment.objects.filter(commentPost=self.kwargs['pk'])
            context['PCC'] = PostCategory.objects.get(pcPost=self.kwargs['pk']).pcCategory
            context['all_category'] = Category.objects.filter(post=self.kwargs.get('pk'))
            context['time'] = datetime.utcnow()
        except Comment.DoesNotExist:
            context['CP'] = None
            context['PCC'] = None
            context['all_category'] = None
        return context

    def get_success_url(self):
        return reverse('news_detail', kwargs={'pk': self.get_object().id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.commentPost = self.get_object()
        comment.commentUser = self.request.user
        comment.save()
        return super().form_valid(form)


# дженерик для создания объекта.
class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'news_create.html'
    form_class = PostForm
    context_object_name = 'new'
    permission_required = 'news.add_post'

    def get_context_data(self, *args, **kwargs):
        context = super(NewsCreateView, self).get_context_data(**kwargs)
        context['all_category'] = Category.objects.filter()
        return context


# для поиска публикаций
class NewsSearchView(LoginRequiredMixin, PermissionRequiredMixin, NewsList):
    template_name = 'search.html'
    permission_required = 'news.add_post'


# дженерик для редактирования объекта
class NewsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'news_update.html'
    form_class = PostForm
    permission_required = 'news.add_post'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления
class NewsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'news_delete.html'
    queryset = Post.objects.all()
    context_object_name = 'new'
    success_url = '/news/'
    permission_required = 'news.add_post'


# =============== По категориям детали =====================================
class NewsCategoryListView(DetailView):
    model = Category
    template_name = 'news_category.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(pk=self.kwargs.get('pk'))
        posts = []
        for i in list(Post.objects.filter(postCategory__category_name=category).order_by('-id')):
            posts.append(i)
        context['posts_in_category'] = posts
        context['all_category'] = Category.objects.all()
        context['is_subscriber'] = Category.objects.get(
            pk=self.kwargs.get('pk')).subscriber.filter(username=self.request.user).exists()
        return context


class Subscriber(UpdateView):
    model = Category

    def post(self, request, *args, **kwargs):
        if not Category.objects.get(pk=self.kwargs.get('pk')).subscriber.filter(username=self.request.user).exists():
            Category.objects.get(pk=self.kwargs.get('pk')).subscriber.add(self.request.user)
        else:
            Category.objects.get(pk=self.kwargs.get('pk')).subscriber.remove(self.request.user)
        return redirect(request.META.get('HTTP_REFERER'))



