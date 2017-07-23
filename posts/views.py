from django.shortcuts import render
from django.http import HttpResponse
from . models import Post
from django.shortcuts import get_object_or_404


# Create your views here.
def post_create(request):
	post_list =  get_object_or_404(Post, id=2)
	context = {
		"user" : request.user,
		"list" :post_list,
	}






	return render(request, 'create.html', context)

def post_update(request):
	return render(request, 'update.html', {})

def post_delete(request):
	return render(request, 'delete.html', {})

def post_list(request):
	return render(request, 'list.html', {})

def post_detail(request):
	return render(request, 'detail.html', {})
