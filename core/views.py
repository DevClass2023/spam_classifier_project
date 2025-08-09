from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import logging # Added logging

from .models import EmailClassification, ClassificationFeedback
from .forms import FeedbackForm

logger = logging.getLogger(__name__) # Initialize logger

# -----------------------
# AUTH VIEWS
# -----------------------

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"New user registered: {user.username}") # Added logging
            return redirect('dashboard')
        else:
            logger.warning(f"Registration failed for username: {request.POST.get('username')}, errors: {form.errors}") # Added logging
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User logged in: {user.username}") # Added logging
            return redirect('dashboard')
        else:
            logger.warning(f"Login failed for username: {request.POST.get('username')}, errors: {form.errors}") # Added logging
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def logout_view(request):
    logger.info(f"User logged out: {request.user.username}") # Added logging
    logout(request)
    return redirect('login')

# -----------------------
# DASHBOARD + CLASSIFY
# -----------------------

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import EmailClassification

@login_required
def dashboard_view(request):
    # Fetch ALL classifications, regardless of the user.
    # This will show emails classified by the Postfix script (user=None).
    all_classifications = EmailClassification.objects.all().order_by('-timestamp')

    paginator = Paginator(all_classifications, 10)

    page_number = request.GET.get('page')
    classifications = paginator.get_page(page_number)

    return render(request, 'core/dashboard.html', {
        'classifications': classifications
    })

@login_required
def classify_email_view(request):
    return render(request, 'core/classify_email.html')

# -----------------------
# FEEDBACK SUBMIT
# -----------------------

@login_required
@require_POST
def submit_feedback(request, classification_id):
    if request.headers.get('content-type') != 'application/json':
        logger.warning(f"Feedback: Expected application/json, got {request.headers.get('content-type')} from user {request.user.username}")
        return JsonResponse({'status': 'error', 'message': 'Expected application/json'}, status=400)

    try:
        data = json.loads(request.body)
        is_correct = data.get('is_correct')
        user_comment = data.get('user_comment', '').strip() # Get user_comment, default to empty string, and strip whitespace
    except json.JSONDecodeError:
        logger.warning(f"Feedback: Invalid JSON from user {request.user.username}: {request.body}")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)

    classification = get_object_or_404(EmailClassification, id=classification_id, user=request.user)

    if classification.is_feedback_provided:
        logger.info(f"Feedback: User {request.user.username} tried to submit duplicate feedback for classification {classification_id}")
        return JsonResponse({'status': 'error', 'message': 'Feedback already submitted.'}, status=400)

    form = FeedbackForm({'is_correct': is_correct, 'user_comment': user_comment})
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.classification = classification
        feedback.save()

        classification.is_feedback_provided = True
        classification.save()

        logger.info(f"Feedback: User {request.user.username} submitted feedback for classification {classification_id}: correct={is_correct}, comment='{user_comment}'")
        return JsonResponse({'status': 'success', 'message': 'Feedback submitted.'})
    else:
        logger.warning(f"Feedback: Form validation failed for user {request.user.username}, classification {classification_id}, errors: {form.errors.as_json()}")
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)