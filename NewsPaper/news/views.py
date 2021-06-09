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
# class NewsCategoryListView(ListView):
#     model = Category
#     template_name = 'news_category.html'
#     context_object_name = 'categorys'

    # def get_success_url(self):
    #     return reverse('news_category', kwargs={'pk': self.get_object().id})
    #
    # def get_context_data(self, *args, **kwargs):
    #     context = super(NewsCategoryListView, self).get_context_data(**kwargs)
    #     context['all_category'] = Category.objects.filter()
    #     context['all_pc_dt'] = Post.objects.filter()
    #     return context


class CategorySubscribe(LoginRequiredMixin, View):
    model = Category
    template_name = 'news_category.html'
    context_object_name = 'new'

    def post(self, request, *args, **kwargs):
        user = self.request.user
        category = get_object_or_404(Category, id=self.kwargs['pk'])
        if category.subscriber.filter(self.request.user).exists():
            category.subscriber.remove(user)
        else:
            category.subscriber.add(user)

        send_mail(
            subject=f'{user}',
            # имя клиента и дата записи будут в теме для удобства
            message=f'Категория на которую вы подписаны {category.category_name}  ',
            # сообщение с кратким описанием проблемы
            from_email='test43@gmail.com',  # здесь указываете почту, с которой будете отправлять (об этом попозже)
            recipient_list=['skillfac@gmail.com']  # здесь список получателей. Например, секретарь, сам врач и т. д.
        )
        return redirect('/')


@login_required
def subscribe_me(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    if category not in user.category_set.all():
        category.subscriber.add(user)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unsubscribe_me(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    if category in user.category_set.all():
        category.subscriber.remove(user)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))
# @login_required
# def subscribe_view(request):
#     """Вьюшка для функционала кнопок Подписаться/Отписаться + Отправка подтверждения Отписки/Подписки юзеру"""
#     category = get_object_or_404(Category, id=request.POST.get('pk'))
#     if category.subscriber.filter(id=request.user.id).exists():
#         category.subscriber.remove(request.user)
#         sub_trigger = False
#     else:
#         category.subscriber.add(request.user)
#         sub_trigger = True
#     html_context_category = {'category_name': category, 'sub_category_user': request.user}
#     if sub_trigger:
#         html_content = render_to_string('mail_notification_subscribe.html', html_context_category)
#         msg = EmailMultiAlternatives(
#             subject=f'Подтверждение подписки на обновления в категории {html_context_category["sub_category_name"]} '
#                     f'(velosiped.test)',
#             from_email='testun_test@mail.ru',
#             to=['skillfac@gmail.com'],
#         )
#         msg.attach_alternative(html_content, "text/html")  # добавляем html
#
#         msg.send()  # отсылаем
#     else:
#         html_content = render_to_string('mail_notification_unsubscribe.html', html_context_category)
#         msg = EmailMultiAlternatives(
#             subject=f'Подтверждение отписки от обновлений в категории {html_context_category["sub_category_name"]}'
#                     f'(velosiped.test)',
#             from_email='testun_test@mail.ru',
#             to=['skillfac@gmail.com'],  # это то же, что и recipients_list
#         )
#         msg.attach_alternative(html_content, "text/html")  # добавляем html
#
#         msg.send()  # отсылаем
#     return redirect('news/')
