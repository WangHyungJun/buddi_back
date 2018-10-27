from django import template
from cebula import models
import pdb
register=template.Library()

@register.filter
def sub_category(things, category):
    try:
        sub_category=models.Category.objects.filter(parentId=category.pk)
    except IndexError:
        return None
    else:
        return sub_category

def transformation(things, input):
    new_input=input.replace(" ", "-")
    return new_input
