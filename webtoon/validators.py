from django.core.exceptions import ValidationError


def isDayName(value):
    dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return value in dayNames
