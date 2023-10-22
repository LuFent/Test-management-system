from django.db.models.signals import pre_delete
from .models import TestFile, ProjectVersion
from django.dispatch import receiver
from shutil import rmtree
import os
from django.conf import settings
from .tools import get_reserve_repo_name, get_repo_path


@receiver(pre_delete, sender=TestFile)
def delete_file(sender, instance, *args, **kwargs):
    try:
        file_path = instance.file_path
        os.remove(file_path)
    except Exception:
        pass


@receiver(pre_delete, sender=ProjectVersion)
def delete_repo(sender, instance, *args, **kwargs):
    repo_path = get_repo_path(instance.project.id, instance.id)
    if os.path.isdir(get_reserve_repo_name(repo_path)):
        try:
            rmtree(get_reserve_repo_name(repo_path))
        except Exception:
            pass
    try:
        rmtree(repo_path)
    except Exception:
        pass
