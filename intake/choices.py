from extras.choices import ChoiceSet


class InterestGroup(ChoiceSet):
    INTERVIEW = 'interview'
    PROGRAMS = 'programs'
    CONNECT = 'connect'
    LEARN = 'learn'

    INTEREST_CHOICES = [
        (INTERVIEW, 'Interview'),
        (PROGRAMS, 'Programs'),
        (CONNECT, 'Connect'),
        (LEARN, 'Learn More'),
    ]
