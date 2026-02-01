from extras.choices import ChoiceSet


class EventStatus(ChoiceSet):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CANCELED = 'canceled'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_CANCELED, 'Canceled'),
    ]


class EventVisibility(ChoiceSet):
    VIS_PUBLIC = 'public'
    VIS_MEMBERS = 'members'
    VIS_PRIVATE = 'private'

    VISIBILITY_CHOICES = [
        (VIS_PUBLIC, 'Public'),
        (VIS_MEMBERS, 'Members'),
        (VIS_PRIVATE, 'Private'),
    ]


class Recurrence(ChoiceSet):
    REC_WEEKLY = 'weekly'
    REC_BIWEEKLY = 'biweekly'
    REC_MONTHLY = 'monthly'

    REC_CHOICES = [
        (REC_WEEKLY, 'Weekly'),
        (REC_BIWEEKLY, 'Every 2 Weeks'),
        (REC_MONTHLY, 'Monthly'),
    ]


class Weekday(ChoiceSet):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    WEEKDAY_CHOICES = [
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    ]


class WeekOfMonth(ChoiceSet):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    LAST = 5

    WEEK_OF_MONTH_CHOICES = [
        (FIRST, "First"),
        (SECOND, "Second"),
        (THIRD, "Third"),
        (FOURTH, "Fourth"),
        (LAST, "Last"),
    ]