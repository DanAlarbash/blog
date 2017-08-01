from django.shortcuts import render, redirect
from django.http import HttpResponse
from . models import Post
from django.shortcuts import get_object_or_404
from .forms import PostForm, UserSignUp, UserLogin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib.parse import quote
from django.http import Http404
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout


def usersignup(request):
	context = {}
	form = UserSignUp()
	context ['form'] = form 
	if request.method == "POST":
		form = UserSignUp(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			username = user.username
			password = user.password
			user.set_password(password)
			user.save()
			auth_user = authenticate(username=username, password=password)
			login(request, auth_user)

			return redirect("posts:list")
		messages.error(request, form.errors)
		return redirect("posts:signup")
	return render(request, 'signup.html', context)

def userlogout(request):
	logout(request)
	return redirect("posts:login")


def userlogin(request):
	context = {}
	form = UserLogin()
	context['form'] = form
	if request.method == "POST":
		form = UserLogin(request.POST)
		if form.is_valid():

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			auth_user = authenticate(username=username, password=password)
			if auth_user is not None:
				login(request, auth_user)
				return redirect("posts:list")

			message.warning(request, "Wrong username/password combination. Please try again.")
			return redirect("posts:login")
		messages.error(request, form.errors)
		return redirect("posts:login")
	return render(request, 'login.html', context)



# Create your views here.
def post_detail(request, slug):
	obj =  get_object_or_404(Post, slug=slug)
	date = timezone.now().date()

	if obj.publish > date or obj.draft:
		if not(request.user.is_staff or request.user.is_superuser):
			raise Http404


	context = {
		"instance": obj,
		#"share_string": quote(obj.content),

	}
	return render(request, 'post_detail.html', context)


def post_list(request):
	today = timezone.now().date()
	
	if request.user.is_staff or request.user.is_superuser:
		obj_list = Post.objects.all()
	else:
		obj_list = Post.objects.filter(draft=False).filter(publish__lte=today)

	query = request.GET.get("q")
	if query:
		obj_list = obj_list.filter(
			Q(title__icontains=query)| #contains if case sensative
			Q(content__icontains=query)|
			Q(author__first_name__icontains=query)|
			Q(author__last_name__icontains=query)
			).distinct()

	paginator = Paginator(obj_list, 4) # Show 8 contacts per page
	page = request.GET.get('page')
	try:
		objs = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		objs = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		objs = paginator.page(paginator.num_pages)

	context = {
		"post_list": objs,
		"today": today,
	}
	return render(request, 'post_list.html', context)

def post_create(request):
	if not (request.user.is_staff or request.user.is_superuser):
		raise Http404
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		obj = form.save(commit=False)
		obj.author = request.user
		obj.save()
		messages.success(request, "OMG! So cool! You created an object.")
		return redirect("posts:list")
	context = {
		"form":form,
	}
	return render(request, 'post_create.html', context)


def post_update(request, slug):
	if not (request.user.is_staff or request.user.is_superuser):
		raise Http404
	post_object = get_object_or_404(Post, slug=slug)
	form = PostForm(request.POST or None, request.FILES or None, instance=post_object)
	if form.is_valid():
		form.save()
		messages.success(request, "Giving it a second thought?")
		return redirect("posts:list")
	context = {
		"form":form,
		"post_object":post_object,
	}
	return render(request, 'post_update.html', context)


def post_delete(request, slug):
	if not (request.user.is_staff or request.user.is_superuser):
		raise Http404
	obj = Post.objects.get(slug=slug).delete()
	messages.warning(request, "Seriosly bro?")
	return redirect("posts:list")
