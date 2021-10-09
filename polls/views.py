"""Create view for ku-polls."""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages

from .models import Question, Choice


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
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results',
                                            args=(question.id,)))
