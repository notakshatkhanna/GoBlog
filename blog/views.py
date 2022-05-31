from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Post, Categories, PostComment
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    cats = Categories.objects.all()
    ordering = ['-date_posted']
    paginate_by = 3

    def get_context_data(self, *args, **kwargs):
        cat_list = Categories.objects.all()
        latestpost_list = Post.objects.all().order_by('-date_posted')[:3]
        context = super(PostListView, self).get_context_data(*args, **kwargs)
        context["cat_list"] = cat_list
        context["latestpost_list"] = latestpost_list
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, *args, **kwargs):
        cat_list = Categories.objects.all()
        latestpost_list = Post.objects.all().order_by('-date_posted')[:3]
        context = super(PostDetailView, self).get_context_data(*args, **kwargs)
        context["cat_list"] = cat_list
        context["latestpost_list"] = latestpost_list
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def search(request):
    template = 'blog/search.html'
    query = request.GET.get('q')
    posts = Post.objects.filter(title__icontains=query)
    params = {'posts': posts}
    return render(request, template, params)


def CategoryView(request, cats):
    if Categories.objects.filter(categoryname=cats).exists():
        category_posts = Post.objects.filter(
            category__categoryname=cats).order_by('-date_posted')
        cat_list = Categories.objects.all()
        latestpost_list = Post.objects.all().order_by('-date_posted')[:3]
        paginator = Paginator(category_posts, 2)
        page = request.GET.get('page')
        category_posts = paginator.get_page(page)
        return render(request, 'blog/category_list.html', {'cats': cats, 'category_posts': category_posts, 'cat_list': cat_list, 'latestpost_list': latestpost_list})
    else:
        raise Http404


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


@login_required(login_url='/login')
def send_comment(request, slug):
    message = request.POST.get('message')
    post_id = request.POST.get('post_id')
    post_comment = PostComment.objects.create(
        sender=request.user, message=message)
    post = Post.objects.filter(id=post_id).first()
    post.comments.add(post_comment)
    if post:
        return HttpResponseRedirect(post.get_absolute_url())
    return redirect(".")
