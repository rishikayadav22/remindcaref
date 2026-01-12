
from django.contrib import admin
from .models import Patient, Prescription, ChatMessage, Snapshot#Reminder

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "age", "room", "created_at")
    search_fields = ("first_name", "last_name", "room")

from django.contrib import admin
from .models import DailyRoutine

@admin.register(DailyRoutine)
class DailyRoutineAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "time", "completed")
    list_filter = ("completed",)

from django.contrib import admin
from .models import FamilyContact

@admin.register(FamilyContact)
class FamilyContactAdmin(admin.ModelAdmin):
    list_display = ("name", "relation", "phone")



from django.contrib import admin
from .models import Routine, RoutineTask


class RoutineTaskInline(admin.TabularInline):
    model = RoutineTask
    extra = 1


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_active")
    inlines = [RoutineTaskInline]





admin.site.register(Prescription)
# admin.site.register(Reminder)
admin.site.register(ChatMessage)
# admin.site.register(Snapshot)


from django.contrib import admin
from .models import EmotionSnapshot
from django.utils.html import format_html

@admin.register(EmotionSnapshot)
class EmotionSnapshotAdmin(admin.ModelAdmin):
    list_display = ('emotion', 'timestamp', 'preview')
    list_filter = ('emotion', 'timestamp')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:100px;"/>', obj.image.url)
        return "-"
    preview.short_description = "Snapshot Preview"
