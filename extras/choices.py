class ChoiceSetMeta(type):
    """
    Metaclass for ChoiceSet
    """
    def __call__(cls, *args, **kwargs):
        # Django will check if a 'choices' value is callable, and if so assume that it returns an iterable
        return getattr(cls, 'CHOICES', ())

    def __iter__(cls):
        choices = getattr(cls, 'CHOICES', ())
        return iter(choices)


class ChoiceSet (metaclass=ChoiceSetMeta):

    CHOICES = list()

    @classmethod
    def values(cls):
        return [c[0] for c in unpack_grouped_choices(cls.CHOICES)]

    @classmethod
    def as_dict(cls):
        # Unpack grouped choices before casting as a dict
        return dict(unpack_grouped_choices(cls.CHOICES))


def unpack_grouped_choices(choices):
    # Unpack a grouped choices hierarchy into a flast list of two-tuples.

    unpacked_choices = []
    for key, value in choices:
        if isinstance(value, (list, tuple)):
            # Entered an optgroup
            for optgroup_key, optgroup_value in value:
                unpacked_choices.append((optgroup_key, optgroup_value))
        else:
            unpacked_choices.append((key, value))
    return unpacked_choices