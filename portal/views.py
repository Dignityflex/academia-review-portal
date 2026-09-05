from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Paper, Review

def paper_list(request):
    """Home page: displays all submitted papers with an optional search filter."""
    query = request.GET.get('q', '').strip()
    if query:
        papers = Paper.objects.filter(title__icontains=query).order_by('-created_at')
    else:
        papers = Paper.objects.all().order_by('-created_at')
    return render(request, 'portal/paper_list.html', {'papers': papers, 'query': query})

def paper_detail(request, pk):
    """View a single paper and allow authenticated users to submit peer reviews."""
    paper = get_object_or_404(Paper, pk=pk)
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
            
        score = request.POST.get('score')
        feedback = request.POST.get('feedback')
        
        # update_or_create ensures one review per user per paper
        Review.objects.update_or_create(
            paper=paper, 
            reviewer=request.user,
            defaults={'score': score, 'feedback': feedback}
        )
        return redirect('paper_detail', pk=pk)
        
    return render(request, 'portal/paper_detail.html', {'paper': paper})

@login_required
def submit_paper(request):
    """Allows an authenticated user to post a research proposal or paper."""
    if request.method == 'POST':
        title = request.POST.get('title')
        abstract = request.POST.get('abstract')
        category = request.POST.get('category')
        pdf_url = request.POST.get('pdf_url', '').strip()

        Paper.objects.create(
            title=title,
            abstract=abstract,
            category=category,
            pdf_url=pdf_url,
            author=request.user
        )
        return redirect('paper_list')
        
    return render(request, 'portal/submit_paper.html')

def signup(request):
    """Custom user registration handler."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('paper_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.contrib.auth.models import User
from django.http import HttpResponse


def create_admin_once(request):
    user, created = User.objects.get_or_create(username='admin')
    user.set_password('AdminPass123!')
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    return HttpResponse("Admin account successfully reset: username: admin | password: AdminPass123!")