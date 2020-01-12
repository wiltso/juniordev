from django.db import models


class Package(models.Model):
    name = models.TextField(default=None, null=True)
    description = models.TextField(default=None, null=True)
    installd = models.BooleanField(default=False)
    dependencies = models.ManyToManyField('self', through = 'DependencyRelation', symmetrical = False)


class DependencyRelation(models.Model):
    source = models.ForeignKey(Package, related_name = 'source', null=True, on_delete=models.CASCADE)#PROTECT)
    target = models.ForeignKey(Package, related_name = 'target', null=True, on_delete=models.CASCADE)


class AlternativesDependencyes(models.Model):
    source_packages = models.ForeignKey(Package, null=True, related_name="source_packages", on_delete=models.CASCADE)
    alternatives = models.ManyToManyField(Package)
