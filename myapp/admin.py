from django.contrib import admin
from .models import Profile, LongTermGoal, YearlyGoal, MonthlyGoal, WeeklyGoal, DailyGoal, Goal,M, W, D, WGoal, DGoal, D1, Objective

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(LongTermGoal)
class LongTermGoalAdmin(admin.ModelAdmin):
    pass

@admin.register(YearlyGoal)
class YearlyGoalAdmin(admin.ModelAdmin):
    pass

@admin.register(MonthlyGoal)
class MonthlyGoalAdmin(admin.ModelAdmin):
    pass

@admin.register(WeeklyGoal)
class WeeklyGoalAdmin(admin.ModelAdmin):
    pass

@admin.register(DailyGoal)
class DailyGoalAdmin(admin.ModelAdmin):
    pass


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    pass


@admin.register(M)
class MAdmin(admin.ModelAdmin):
    pass

@admin.register(W)
class WAdmin(admin.ModelAdmin):
    pass

@admin.register(D)
class DAdmin(admin.ModelAdmin):
    pass

@admin.register(WGoal)
class WGoalAdmin(admin.ModelAdmin):
    pass

@admin.register(DGoal)
class DGoalAdmin(admin.ModelAdmin):
    pass

@admin.register(D1)
class D1Admin(admin.ModelAdmin):
    pass

@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    pass
