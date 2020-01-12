from django.shortcuts import render
from datetime import datetime
from .models import Package, DependencyRelation, AlternativesDependencyes
import subprocess
import re
from django.db.models import Q
from django.http import HttpResponse, JsonResponse


# Create your views here.
lastModifyedDate = datetime.now()

def home(request):
    statusFileUpdated()
    packages = Package.objects.filter(installd=True).values('name').order_by('name')
    return render(request, 'main/home.html', {"pakages": packages})


def packageView(request, name):
    statusFileUpdated()
    try:
        package = Package.objects.get(name=name)
    except:
        return HttpResponse("<h1>Packages dose not exist</h1>")

    dependentOn = Package.objects.filter(id__in=DependencyRelation.objects.filter(target=package).values("source_id"))
    altt = AlternativesDependencyes.objects.filter(source_packages=package)
    dependencyes = [package.dependencies.filter(installd=True).order_by("name")]
    alt_dependencies =[]
    for alte in altt:
        dependencyes.append(Package.objects.filter(Q(id__in=alte.alternatives.all()) & Q(installd=True)).order_by("name"))
    print(dependencyes)

    varibels = {
        "package": package,
        "dependencies": dependencyes,
        "dependentOn": dependentOn
    }

    return render(request, 'main/packagesView.html', varibels)


# Checks if the statu file has been update
# Runs when load any page
def statusFileUpdated():
    modifycationTime = subprocess.check_output('stat /var/lib/dpkg/status | grep "Modify"', shell=True)
    modifycationTime = modifycationTime[8:-6]
    modifyedDate = datetime.strptime(modifycationTime, '%Y-%m-%d %H:%M:%S.%f')
    if lastModifyedDate < modifyedDate:
        lastModifyedDate = modifyedDate
        updateDB()


def removeVersion(dependency):
    return re.split(' \(.*?\)|:any', dependency)[0]


def updateDB():
    with open('/var/lib/dpkg/status') as f:
        packageList = f.read()
    packageList = packageList.split('\n\n')[:-1]
    relations = {}
    
    installdPackages = list(Package.objects.all().values_list("name", flat=True))

    for package in packageList:

        splitedPackage = package.split('\n')

        name = splitedPackage[0][9:]
        dependencies = [item.split("epends: ")[1] for item in splitedPackage if re.search("Depends: *", item)]
        descriptionStart = [index for index, item in enumerate(splitedPackage) if  re.search("Description: *", item)][0]
        descriptionEnds = int()
        for index, item in enumerate(splitedPackage):
            if re.search("^[A-Z]", item) and (index > descriptionStart or index == len(splitedPackage)):
                descriptionEnds = index
                break

        description = splitedPackage[descriptionStart][13:] + "\n"
        description += "\n".join(splitedPackage[descriptionStart+1:descriptionEnds])

        try:
            installdPackages.remove(name)
        except ValueError:
            pass
        
        packObject, created = Package.objects.get_or_create(name=name)
        if created or packObject.installd == False:
            packObject.description = description
            packObject.installd = True
            packObject.save()
            try:
                dependencies = re.split(", ", ", ".join(dependencies))
                for dependency in dependencies:
                    if " | " in dependency:
                        dependency = dependency.split(" | ")
                        alternativObject = AlternativesDependencyes(source_packages=packObject)
                        alternativObject.save()

                        for index, alternativ in enumerate(dependency):
                            alternativ = removeVersion(alternativ)
                            dependencyObject, dependencyCreated = Package.objects.get_or_create(name=alternativ)
                            if dependencyCreated:
                                dependencyObject.save()
                            alternativObject.alternatives.add(dependencyObject)
                        alternativObject.save()
                    else:
                        dependency = removeVersion(dependency)
                        dependencyObject, dependencyCreated = Package.objects.get_or_create(name=dependency)
                        if dependencyCreated:
                            dependencyObject.save()
                        packObject.dependencies.add(dependencyObject)
            except IndexError:
                pass
            
            packObject.save()
    
    for installPackage in installdPackages:
        packObject = Package.objects.get(name=installPackage)
        packObject.installd = False
        packObject.save()
