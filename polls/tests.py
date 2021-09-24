import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from  .models import Question


class QuestionModelTests(TestCase):

    def test_is_published_true(self):
        time = timezone.now() - datetime.timedelta(days= 2)
        question = Question(pub_date=time)

        self.assertIs(question.is_published(), True)

    def test_is_published_false(self):
        time = timezone.now() + datetime.timedelta(days= 20)
        question = Question(pub_date=time)

        self.assertIs(question.is_published(), False)

    def test_can_vote_now(self):
        time = timezone.now()
        times = timezone.now() + datetime.timedelta(days= 2)
        question = Question(pub_date=time, end_date = times)

        self.assertIs(question.can_vote(), True)

    def test_can_vote_now_end_date_pass(self):
        time = timezone.now()
        times = timezone.now() - datetime.timedelta(days= 2)
        question = Question(pub_date=time, end_date = times)

        self.assertIs(question.can_vote(), False)

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days = 30)
        times = timezone.now() + datetime.timedelta(days=365)
        future_question = Question(pub_date = time, end_date = times)

        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days = 1, seconds= 1)
        times = timezone.now() + datetime.timedelta(days=365)
        old_question = Question(pub_date = time, end_date = times)

        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours = 23, minutes = 59, seconds = 59)
        times = timezone.now() + datetime.timedelta(days = 365)
        recent_question = Question(pub_date = time, end_date = times)

        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days = days)
    return Question.objects.create(question_text = question_text, pub_date = time, end_date = time + datetime.timedelta(days =10))

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", days= -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past question.>'])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past question.>'])

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question 2.>', '<Question: Past question 1.>'])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question',days= 5)
        url = reverse('polls:detail', args=(future_question.id, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question', days=-5)
        url = reverse('polls:detail', args = (past_question.id, ))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_after_end_date(self):
        """
        this test when vote time is out. Check can vote or not.
        """
        end_question = create_question(question_text='End Question', days=-10)
        url = reverse('polls:detail', args=(end_question.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse('polls:index'), status_code=302,
                             target_status_code=200)


