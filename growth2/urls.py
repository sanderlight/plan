"""
URL configuration for growth2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from django.urls import path


urlpatterns = [
    path("admin/", admin.site.urls),
    path('/', views.index, name='index'),
    
    path('generate_long_term_goal', views.generate_long_term_goal, name='generate_long_term_goal'),
    path('login/', views.user_login, name='login'),
    path("register/", views.register, name='register'),
    path('long_term_goal/', views.generate_long_term, name='long_term_goal'),
    path('option_selection/', views.generate_options, name='generate_options'),
    path('goal_display/', views.generate_long_term_goals, name='generate_long_term_goals'),
    path('year_plan/', views.generate_year_plan, name='generate_year_plan'),
    path('month/<int:id>/', views.generate_month_to_month_plans_view, name='generate_month_to_month_plans'),
     path('week/<int:id>', views.generate_week_to_week_plans_view, name='generate_week_to_week_plans'),
    path('daily_goals/<int:id>/', views.daily_goal_view, name='daily_goals'),
    path('profile/', views.profile_view, name='profile'),
    path('day/', views.daily_goal_detail_view, name='day'),
     path('update-daily-goal-status/<int:id>/', views.update_daily_goal_status_view, name='update_daily_goal_status'),
    path('analytics/', views.analytics_view, name='analytics'),
     path('goal-simulation/', views.goal_simulation, name='goal_simulation'),
    path('api/analytics/', views.analytics_data_view, name='analytics_data'),
     path('generate-goals/', views.generate_goals, name='generate_goals'),
    path('get-yearly-goal-dates/', views.get_yearly_goal_dates_view, name='get_yearly_goal_dates'),
    path('api/yearly_goals/', views.get_yearly_goals, name='get_yearly_goals'),
    path('api/monthly_goals/', views.get_monthly_goals, name='get_monthly_goals'),
    path('api/weekly_goals/', views.get_weekly_goals, name='get_weekly_goals'),
    path('api/daily_goal/', views.get_daily_goal, name='get_daily_goals'),
    path('goals/yearly/details/', views.get_yearly_goal_details, name='get_yearly_goal_details'),
    path('goals/monthly/details/', views.get_monthly_goal_details, name='get_monthly_goal_details'),
    path('goals/weekly/details/', views.get_weekly_goal_details, name='get_weekly_goal_details'),
    path('goals/daily/details/', views.get_daily_goal_details, name='get_daily_goal_details'),
    path('land/', views.year_to_day_view, name='year_to_day'),
    path('months/', views.generate_month_plan, name='generate_month_plan'),
     path('week-goal/', views.generate_week_to_week_plan, name='generate_week_to_week_plan'),
     path('week-to-day/<int:week_goal_id>/', views.generate_week_to_day_plan, name='generate_week_to_day_plan'),
    path('month-to-week/<int:id>/', views.generate_week_plan_from_month, name='generate_week_plan_from_month'),
    
    
    
    path('get_monthly_goals/', views.get_monthly_goals, name='get_monthly_goals'),
    path('get_weekly_goals/', views.get_weekly_goals, name='get_weekly_goals'),
    path('get_daily_goals/', views.get_daily_goals, name='get_daily_goals'),
    path('get_wgoal_details/', views.get_wgoal_details, name='get_wgoal_details'),
    path('get_dgoal_details/', views.get_dgoal_details, name='get_dgoal_details'),
    path('get_d1_goals/', views.get_d1_goals, name='get_d1_goals'),
    
    
    
    
    
    
    
    
    path('month-to-day/<int:id>/', views.generate_day_plan_from_month, name='generate_day_plan_from_month'),

   path('day-goal/', views.generate_day_plan, name='generate_day_plan'),
     path('setup_goal/', views.setup_goal_view, name='setup_goal'),




   
]
     

