from datetime import date, timedelta
from filters import qand, qor, CascadeFilter, qsfilter
from django.db.models import Q

from polls.models import Question

class most_recent(CascadeFilter):

    class filter(qand):
        text = Q(question_text__icontains='what')

        day_ago = date.today() - timedelta(days=1)
        pub_date = Q(pub_date__gt=day_ago)

    @qsfilter
    def order(qs):
        return qs.order_by('-pub_date')

    @qsfilter
    def take_two(qs):
        if qs.exists():
            return qs[:2]


questions = most_recent.filter(Question.objects.all())
print(questions)
