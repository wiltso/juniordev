from django.db import models


# Every package that is installd will get a name, description and installed = true
# If a package is just named as a dependency it will just get the name and installed = False
# Packages can't be deleted they can just be uninstalled
# Meaning installed = False and it won't be a link on the front
class Package(models.Model):
    name = models.TextField(default=None, null=True)
    description = models.TextField(default=None, null=True)
    installd = models.BooleanField(default=False)
    version = models.TextField(default=None, null=True)
    dependencies = models.ManyToManyField("self",
                                          through="DependencyRelation",
                                          symmetrical=False)


# All dependencyes that dosen't have other options that can be used insted of that dependency
# Will be related throug this tabel
# The source is the package and the target is the package's dependency package
# Read more in the readme file under Dependency Relation
class DependencyRelation(models.Model):
    source = models.ForeignKey(Package,
                               related_name="source",
                               null=True,
                               on_delete=models.PROTECT)

    target = models.ForeignKey(Package,
                               related_name="target",
                               null=True,
                               on_delete=models.PROTECT)


# If a there are alternative dependencys for a package the relation will be connected here
# The source_package is the package that has this dependencys
# The alternatives ManyToManyFiled will have the options for the dependencyes
# Read more in the readme file under Alternative Dependencyes
class AlternativesDependencyes(models.Model):
    source_packages = models.ForeignKey(Package,
                                        null=True,
                                        related_name="source_packages",
                                        on_delete=models.PROTECT)

    alternatives = models.ManyToManyField(Package)
