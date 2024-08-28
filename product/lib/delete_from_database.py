from ..models import *


def delete_from_database(model):
    delete_model = model
    delete_model.objects.all().delete()
