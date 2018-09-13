from django.contrib import admin
from .models import *
from rangefilter.filter import DateRangeFilter
# django-import-export
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# ----- django-import-export Models -----

class JobResource(resources.ModelResource):
    class Meta:
        model = Job

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Job

class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization

# ----- Admin Models -----

class JobAdmin(ImportExportModelAdmin):
    model = Job
    list_filter = (('date_created', DateRangeFilter),
                   'closed',
                   'organizations__name',
                   'categories',
                   'duedate',
    )

    list_display = ('name',
                    'closed',
                    'duedate',
                    'status',
    )

    resource_class = JobResource

class CategoryAdmin(ImportExportModelAdmin):
    model = Category
    list_filter = ('group__name',)

    resource_class = CategoryResource

class OrganizationAdmin(ImportExportModelAdmin):
    model = Organization
    list_filter = ('categories',
                   'available',
    )
    list_display = ('name',
                    'available',
    )

    resource_class = OrganizationResource


admin.site.register(Job,JobAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(CategoryGroup)
admin.site.register(Organization,OrganizationAdmin)
