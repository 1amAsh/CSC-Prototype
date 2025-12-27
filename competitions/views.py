from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Competition, Problem, Submission
from .forms import CompetitionForm, ProblemForm, SubmissionForm, ScoreForm

def admin_required(view_func):
    """Decorator to check if user is admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        if not request.user.is_admin:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def competition_list(request):
    """List all competitions"""
    competitions = Competition.objects.all()
    context = {'competitions': competitions}
    return render(request, 'competitions/list.html', context)

@login_required
def competition_detail(request, pk):
    """View competition details and problems"""
    competition = get_object_or_404(Competition, pk=pk)
    problems = competition.problems.all()
    
    # Check if user has submitted
    user_submission = None
    if not request.user.is_admin:
        try:
            user_submission = Submission.objects.get(competition=competition, user=request.user)
        except Submission.DoesNotExist:
            pass
    
    context = {
        'competition': competition,
        'problems': problems,
        'user_submission': user_submission,
    }
    return render(request, 'competitions/detail.html', context)

@login_required
def competition_leaderboard(request, pk):
    """View competition leaderboard"""
    competition = get_object_or_404(Competition, pk=pk)
    leaderboard = competition.leaderboard
    
    context = {
        'competition': competition,
        'leaderboard': leaderboard,
    }
    return render(request, 'competitions/leaderboard.html', context)

@admin_required
def competition_create(request):
    """Create new competition"""
    if request.method == 'POST':
        form = CompetitionForm(request.POST)
        if form.is_valid():
            competition = form.save(commit=False)
            competition.created_by = request.user
            competition.save()
            messages.success(request, 'Competition created successfully!')
            return redirect('competitions:detail', pk=competition.pk)
    else:
        form = CompetitionForm()
    
    return render(request, 'competitions/create.html', {'form': form})

@admin_required
def competition_edit(request, pk):
    """Edit competition"""
    competition = get_object_or_404(Competition, pk=pk)
    
    if request.method == 'POST':
        form = CompetitionForm(request.POST, instance=competition)
        if form.is_valid():
            form.save()
            messages.success(request, 'Competition updated successfully!')
            return redirect('competitions:detail', pk=pk)
    else:
        form = CompetitionForm(instance=competition)
    
    return render(request, 'competitions/edit.html', {'form': form, 'competition': competition})

@admin_required
def competition_delete(request, pk):
    """Delete competition"""
    competition = get_object_or_404(Competition, pk=pk)
    
    if request.method == 'POST':
        competition.delete()
        messages.success(request, 'Competition deleted successfully!')
        return redirect('competitions:list')
    
    return render(request, 'competitions/delete.html', {'competition': competition})

@admin_required
def problem_add(request, competition_pk):
    """Add problem to competition"""
    competition = get_object_or_404(Competition, pk=competition_pk)
    
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.competition = competition
            problem.save()
            messages.success(request, 'Problem added successfully!')
            return redirect('competitions:detail', pk=competition_pk)
    else:
        form = ProblemForm()
    
    return render(request, 'competitions/problem_add.html', {'form': form, 'competition': competition})

@login_required
def submit_solution(request, pk):
    """Submit solution for competition"""
    competition = get_object_or_404(Competition, pk=pk)
    
    # Check if already submitted
    existing_submission = Submission.objects.filter(competition=competition, user=request.user).first()
    
    if request.method == 'POST':
        if existing_submission:
            form = SubmissionForm(request.POST, instance=existing_submission)
        else:
            form = SubmissionForm(request.POST)
        
        if form.is_valid():
            submission = form.save(commit=False)
            submission.competition = competition
            submission.user = request.user
            submission.save()
            
            if existing_submission:
                messages.success(request, 'Submission updated successfully!')
            else:
                messages.success(request, 'Submission submitted successfully!')
            
            return redirect('competitions:detail', pk=pk)
    else:
        if existing_submission:
            form = SubmissionForm(instance=existing_submission)
        else:
            form = SubmissionForm()
    
    context = {
        'form': form,
        'competition': competition,
        'existing_submission': existing_submission,
    }
    return render(request, 'competitions/submit.html', context)

@admin_required
def submissions_list(request, pk):
    """View all submissions for a competition"""
    competition = get_object_or_404(Competition, pk=pk)
    submissions = competition.submissions.select_related('user').all()
    
    context = {
        'competition': competition,
        'submissions': submissions,
    }
    return render(request, 'competitions/submissions.html', context)

@admin_required
def score_submission(request, pk):
    """Score a submission"""
    submission = get_object_or_404(Submission, pk=pk)
    
    if request.method == 'POST':
        form = ScoreForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.scored_by = request.user
            submission.scored_at = timezone.now()
            submission.save()
            
            # Update ranks
            update_competition_ranks(submission.competition)
            
            messages.success(request, 'Submission scored successfully!')
            return redirect('competitions:submissions', pk=submission.competition.pk)
    else:
        form = ScoreForm(instance=submission)
    
    context = {
        'form': form,
        'submission': submission,
    }
    return render(request, 'competitions/score.html', context)

def update_competition_ranks(competition):
    """Update ranks for all submissions in a competition"""
    submissions = list(competition.submissions.order_by('-score', 'submitted_at'))
    
    current_rank = 1
    for i, submission in enumerate(submissions):
        submission.rank = current_rank
        submission.save(update_fields=['rank'])
        
        # If next submission has different score, increment rank
        if i + 1 < len(submissions) and submissions[i + 1].score < submission.score:
            current_rank = i + 2