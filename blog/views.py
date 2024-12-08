from django.utils import timezone
from .models import Post
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from django.http import HttpResponse
import uuid
# Create your views here.
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})
def post_detail(request, pk):
    Post.objects.get(pk=pk)
    post = get_object_or_404(Post, pk=pk)
    user_token = request.COOKIES.get('user_token')
    print(f"User Authenticated: {request.user.is_authenticated}")
    print(f"User Token (from cookies): {user_token}")
    print(f"Post Token: {post.token}")
    print(f"Tokens Match: {post.token == user_token}")
    
    if not request.user.is_authenticated:
        print("Anonymous User Check:")
        print(f"post.token == user_token: {post.token == user_token}")
        
    can_edit_delete = (
        request.user.is_superuser or 
        (request.user.is_authenticated and post.author == request.user) or 
        (not request.user.is_authenticated and post.token == user_token)
    )
    
    print(f"Can Edit/Delete: {can_edit_delete}")
    return render(request, 'blog/post_detail.html', {'post': post, 'user_token': user_token, 'can_edit_delete': can_edit_delete})
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            if request.user.is_authenticated:
                post.author = request.user
            else:
                token = request.COOKIES.get('user_token')
                if not token:
                    token = str(uuid.uuid4())
                post.token = token
                print(f"Generated Token: {token}")
            post.published_date = timezone.now()
            post.save()
            
            response = redirect('post_detail', pk=post.pk)
            if not request.COOKIES.get('user_token'):
                response.set_cookie('user_token', token)
            return response
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})
def post_edit(request, pk):
    user_token = request.COOKIES.get('user_token')
    post = get_object_or_404(Post, pk=pk)
    print(f"User: {request.user}")
    print(f"User Authenticated: {request.user.is_authenticated}")
    print(f"User Token: {user_token}")
    print(f"Post Token: {post.token}")
    print(f"Post Author: {post.author}")
    if pk:
        is_edit = True
    else:
        post = None
        is_edit = False
    if request.user.is_superuser or post.author == request.user or (not request.user.is_authenticated and post.token == user_token):
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.published_date = timezone.now()
                post.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form, 'is_edit': is_edit})
    else:
        return HttpResponse("You do not have permission to edit this post", status=403)
def post_delete(request, pk):
    user_token = request.COOKIES.get('user_token')
    post = get_object_or_404(Post, pk=pk)
    print(f"User: {request.user}")
    print(f"User Authenticated: {request.user.is_authenticated}")
    print(f"User Token: {user_token}")
    print(f"Post Token: {post.token}")
    print(f"Post Author: {post.author}")
    if request.user.is_superuser:
        print("Admin is deleting the post.")
    if post.author == request.user:
        print("Author is deleting the post.")
    if post.token == user_token:
        print("Anonymous user is deleting the post.")
    if request.user.is_superuser or post.author == request.user or (not request.user.is_authenticated and post.token == user_token):
        if request.method == "POST":
            post.delete()
            return redirect('post_list')
        return render(request, 'blog/post_confirm_delete.html', {'post': post})
    else:
        return HttpResponse("You do not have permission to delete this post", status=403)

    