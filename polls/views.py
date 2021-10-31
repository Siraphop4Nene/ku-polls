"""Create view for ku-polls."""
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.utils import timezone
from django.contrib import messages

from .models import Question, Choice, Vote


class IndexView(generic.ListView):
    """Class for IndexView."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()
                                       ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """Class for DetailView."""

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        """Render if can_vote redirect if cant vote."""
        self.object = self.get_object()
        if self.object.can_vote():
            return render(request, self.template_name, self.get_context_data())
        else:
            messages.error(request, 'Vote is not allowed')
            return redirect('polls:index')


class ResultsView(generic.DetailView):
    """Class for ResultsView."""

    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    """Keep vote result for question."""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request,
                      'polls/detail.html',
                      {'question': question,
                       'error_message': "You didn't select a choice.",
                       })
    else:
        user = request.user
        user_vote = get_vote_for_user(user, question)

        if user_vote is None:
            # Create vote.
            user_vote = Vote.objects.create(user=user, choice=selected_choice)
        else:
            # Modify existing vote.
            user_vote.choice = selected_choice

        user_vote.save()
        return redirect('polls:results', question.id)


def get_vote_for_user(user, question):
    """
    Find and return an existing vote for a user on a poll question.
    Returns:
        The user's vote or None if there are no votes for this question.
    """
    try:
        votes = Vote.objects.filter(user=user).filter(choice__question=question)
        if votes.count() == 0:
            return None
        return votes[0]
    except Vote.DoesNotExist:
        return None
