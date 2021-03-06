from django.db.models import Q
from django.shortcuts import render
from main.models import Package, DependencyRelation, AlternativesDependencyes
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
import subprocess
import re


# Create your views here.

# The home page where all the install packages are listed
def home(request):
    statusFileUpdated()
    packages = Package.objects.filter(installd=True).order_by('name')
    return render(request, 'main/home.html', {"pakages": packages})


# The view for when you are viewing a package
# Where the name, description, dependencye's and dependent on is displayed
def packageView(request, name):
    # Checks if the file has been updated
    statusFileUpdated()

    # Trys to get the package that is asked for if it fail to get the package
    # It will render the error page
    try:
        package = Package.objects.get(Q(name=name) & Q(installd=True))
    except Package.DoesNotExist:
        return HttpResponse("<h1>" + name + " is not installed</h1><a href=\"/\">All packages</a>")

    # Get's all of the package that depend on the package that was asked for
    dependentOn = Package.objects.filter(
        id__in=DependencyRelation.objects.filter(
            target=package
        ).values("source_id")
    ).order_by("name")

    # Get's all of the dependencys that has other alternatives dependencyes
    allAlternatives = AlternativesDependencyes.objects.filter(source_packages=package)

    # The dependencyes are in a 2D array for the fornt end to render them correctly easyler
    dependencyes = package.dependencies.all().order_by("name")

    alternativePackages = []
    # Goes true all the alternatives and addes them in to the array
    # Read more about how and way like this in the readme file under Dependency Rendering
    for alternative in allAlternatives:
        alternativePackages.append(
            Package.objects.filter(
                id__in=alternative.alternatives.all()
            ).order_by("name")
        )
    print(alternativePackages, dependencyes)
    varibels = {
        "package": package,
        "dependencies": dependencyes,
        "alternatives": alternativePackages,
        "dependentOn": dependentOn,
    }

    return render(request, 'main/packagesView.html', varibels)


# Checks if the statu file has been update since the database was update
# Runs when load any page
def statusFileUpdated():
    # Gets the the modifyed datetime of the file
    modifycationTime = subprocess.check_output('stat ' + settings.STATUS_PATH + ' | grep "Modify"',
                                               shell=True)

    # Removes the some extra things from the date
    modifycationTime = modifycationTime[8:-10]

    modifyedDate = datetime.strptime(modifycationTime.decode(), '%Y-%m-%d %H:%M:%S.%f')

    # The last modifyed date is stored in the settings file
    # And yes it needs to be all capital letters
    if settings.LAST_MODIFYED_DATE < modifyedDate:
        settings.LAST_MODIFYED_DATE = modifyedDate
        updateDB()


# Removes the version from all dependencyes
def removeVersion(dependency):
    return re.split(' \(.*?\)|:any', dependency)[0]


# Adds the dependencyes to the packObject and save it
def addDependencyes(packObject, dependencies):
    # Joins the dependency's and pre-dependencys together
    # Then splits the the hole string in to all of the dependencyes
    dependencies = re.split(", ", ", ".join(dependencies))
    for dependency in dependencies:
        # If it's a empty dependency it will move on to the next
        if dependency == "":
            continue

        # If there are alternative depdendencyes the if will be true
        if " | " in dependency:
            # Splits the string of alternatives dependencys to an array
            dependency = dependency.split(" | ")

            # Creats a new AlternativeDependency object
            alternativObject = AlternativesDependencyes(source_packages=packObject)
            # The alternativObjects need to get it's autoincrementing id for later
            alternativObject.save()

            # Goes true all of the alternative dependencyes
            # And adds them to the alternativeDependency object
            for index, alternativ in enumerate(dependency):
                alternativ = removeVersion(alternativ)

                # Trys to get the Package of the dependency else it creates it
                dependencyObject, dependencyCreated = Package.objects.get_or_create(name=alternativ)
                # Saves dependecy package if it got created
                if dependencyCreated:
                    dependencyObject.save()

                # Adds the alternative dependency to the alternativObject
                alternativObject.alternatives.add(dependencyObject)

            # Saves the alternativObject with all of the dependencyes
            alternativObject.save()

        else:
            # If there are no alternative it will just add the dependency package to the Package
            dependency = removeVersion(dependency)
            dependencyObject, dependencyCreated = Package.objects.get_or_create(name=dependency)
            # If dependency package is created it needs to be saved to get is's id
            if dependencyCreated:
                dependencyObject.save()
            packObject.dependencies.add(dependencyObject)

    packObject.save()


# Updates the database form the status file
def updateDB():
    with open(settings.STATUS_PATH) as f:
        packageList = f.read()

    # Splist the data from the file into a array of of all the packages
    # There is an empty line between all the packages and the file ends with 2 empty lines
    packageList = packageList.split('\n\n')[:-1]

    # Get's all of the packages so it looks throuh if there are packages that have been uninstalled
    installdPackages = list(Package.objects.all().values_list("name", flat=True))

    for package in packageList:
        # If there is nothing in the package the code will break further down
        # If it dosen't move on to the next
        if package == "":
            continue

        splitedPackage = package.split('\n')

        # Get's the name of the package
        # It is always the first item
        # it alsow removes the "Package: " from the name
        name = splitedPackage[0][9:]

        # Try to remove the package from the array
        # If the item isn't in the list it's just a new package
        try:
            installdPackages.remove(name)
        except ValueError:
            pass

        # Get's all dependensyes that need to be installed even the Pre-Depends:
        # It gose true all of the items in the splitedPackage array
        # If "Depends: " is in the line it will split the line so we only get the dependencyes
        # Then all of the dependencyes from that line will be in the second index
        dependencies = [item.split("epends: ")[1] for item in splitedPackage if "Depends: " in item]

        version = [item.split("ersion: ")[1] for item in splitedPackage if item.startswith(
            "Version: "
        )][0]

        # Get the index of were the first description line is
        descriptionStart = [i for i, item in enumerate(splitedPackage) if item.startswith(
            "Description: "
        )][0]
        descriptionEnds = int()

        # Removing the extra items that is not needed
        splitedPackage = splitedPackage[descriptionStart:]
        for i, item in enumerate(splitedPackage[1:]):
            # To find where the description ends it gose true all the lines,
            # After were the description starts
            # Becouse the description is indented we check if the first chr is a space
            # If not thats where it ends

            if i == len(splitedPackage) or not item.startswith(" "):
                descriptionEnds = i
                break

        # Removes the "Description: " from the first line
        # Then adds the text back together as it was in the status file
        description = splitedPackage[0][13:] + "\n"
        description += "\n".join(splitedPackage[1:descriptionEnds])

        # Trys to get the package from the database if it's not there we create it
        packObject, created = Package.objects.get_or_create(name=name)

        # If the packObject was created or has been created befor but not installed until now
        # It will make that package installd en add the description
        if created or packObject.installd is False:
            # Adds the description and that is installed
            # Then saves the package so it get's it's auto incrementing id
            # Neede further down
            packObject.description = description
            packObject.installd = True
            packObject.version = version
            packObject.save()
            addDependencyes(packObject, dependencies)

        # If the versions of the package is not the same as befor it will create the
        # Dependencyes again and delete the old ones and rewrite the description
        elif packObject.version != version:
            packObject.description = description
            packObject.version = version

            DependencyRelation.objects.filter(source=packObject).delete()
            AlternativesDependencyes.objects.filter(source_packages=packObject).delete()

            addDependencyes(packObject, dependencies)

    # If there are any packages that have been installed
    # But now are uninstalled the will be uninstall but not deleted
    for installPackage in installdPackages:
        packObject = Package.objects.get(name=installPackage)
        packObject.installd = False
        packObject.save()
