from django.db import models
from django.contrib.auth.models import User
import datetime
from datetime import timedelta
from django.utils import timezone
import uuid
# Create your models here.


class Profile(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('Free', 'Free'),
        ('Paid', 'Paid'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default='Free')
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    
    # New fields for goal purchase tracking
    goals_purchased = models.PositiveIntegerField(default=0)  # Number of goals bought individually
    goals_used = models.PositiveIntegerField(default=0)  # Number of goals created so far
    
    def __str__(self):
        return f"{self.user.username}'s Profile - {self.subscription_type}"

    def has_unlimited_subscription(self):
        """Check if the user has an active unlimited subscription."""
        return self.subscription_type == 'Paid' and self.subscription_end_date >= timezone.now().date()

    def has_remaining_goals(self):
        """Check if the user has remaining goals available to use."""
        return self.goals_purchased > self.goals_used
    
class GoalPurchase(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    goals_purchased = models.PositiveIntegerField(default=0)  # Number of goals purchased in this transaction
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)  # Optional expiration date if goals need to expire

    def __str__(self):
        return f"{self.profile.user.username} purchased {self.goals_purchased} goals on {self.purchase_date}"

    
    
class Goal(models.Model):
    goal_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,default=None)

    def __str__(self):
        return self.goal_text

    
    
class GeneratedGoal(models.Model):
    user_response = models.ForeignKey(Goal, on_delete=models.CASCADE)
    goal_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,default=None)




    
class YearlyGoal(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.PositiveIntegerField()
    title = models.CharField(max_length=100, default="Default Title" )
    start_date = models.DateField(default=datetime.date.today)

    

class LongTermGoal(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,default=None)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description[:50]  #
    
    
    
class MonthlyGoal(models.Model):
    yearly_goal = models.ForeignKey(YearlyGoal, on_delete=models.CASCADE, null=True, blank=True, default=None)
  
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    month = models.PositiveIntegerField()



class WeeklyGoal(models.Model):
    yearly_goal = models.ForeignKey(YearlyGoal, on_delete=models.CASCADE, default=None)  # Add a ForeignKey to YearlyGoal
    monthly_goal = models.ForeignKey(MonthlyGoal, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    week = models.PositiveIntegerField()
    week_sequence = models.IntegerField(default=1)
    week_id = models.CharField(max_length=30, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.week_id:
            # Generate a unique week ID in the format: "profile_id-year-yearly_goal_id-week_number"
            self.week_id = f"{self.yearly_goal.profile.id}-{self.yearly_goal.year}-{self.yearly_goal.id}-W{self.week}"
        super().save(*args, **kwargs)

class DailyGoal(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    yearly_goal = models.ForeignKey(YearlyGoal, on_delete=models.CASCADE)
    monthly_goal = models.ForeignKey(MonthlyGoal, on_delete=models.CASCADE)
    weekly_goal = models.ForeignKey(WeeklyGoal, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    completed = models.BooleanField(default=False) 
    
    
    

class UserAnalyticsData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
   
    goal_progress = models.FloatField(default=0.0)
    days_left = models.IntegerField(default=0)
    goal_status = models.CharField(max_length=20, default='green')  # Assuming limited set of statuses
    performance = models.IntegerField(default=0)
    today_completed = models.BooleanField(default=False)

    # Additional fields or methods as needed

    def __str__(self):
        return f'{self.user.username} - {self.goal.name} Analytics'

    class Meta:
        verbose_name_plural = 'User Analytics Data'


DEFAULT_PROFILE_ID = 1

class M(models.Model):  # Renamed from MonthlyGoal
   
    month_number = models.IntegerField()
    month_description = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=DEFAULT_PROFILE_ID)
    start_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"Month {self.month_number}: {self.month_description}"


class W(models.Model):  
    month_goal = models.ForeignKey('M', on_delete=models.CASCADE, null=True)

    week_number = models.IntegerField()
    week_description = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=DEFAULT_PROFILE_ID)
    start_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"Week {self.week_number}: {self.week_description}"


class D(models.Model):  # Renamed from DailyGoal
    week_goal = models.ForeignKey('W', on_delete=models.CASCADE, null=True)

    day_number = models.IntegerField()
    day_description = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=DEFAULT_PROFILE_ID)
    start_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"Day {self.day_number}: {self.day_description}"
    
    
class WGoal(models.Model):
    goal_text = models.CharField(max_length=255)
   
    week_number = models.PositiveIntegerField()
    week_description = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=DEFAULT_PROFILE_ID)
    start_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"Week {self.week_number} - {self.goal_text}"

# Daily Goal Model
class DGoal(models.Model):
    weekly_goal = models.ForeignKey(WGoal, on_delete=models.CASCADE, related_name='daily_goals')
    day_number = models.PositiveIntegerField()
    day_description = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=DEFAULT_PROFILE_ID)
    start_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"Day {self.day_number} for {self.weekly_goal}"
    
    


class D1(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    completed = models.BooleanField(default=False)
    
    start_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"{self.title} on {self.date}"
    
    
    
    
    
class Objective(models.Model):
    """
    Represents an objective setup by the user, including only the timeframe details.
    """
    profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='objectives')
    timeframe_unit = models.CharField(
        max_length=10,
        choices=[
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
            ('years', 'Years')
        ],
        default='months',
        help_text="The unit of time (days, weeks, months, years) for the timeframe."
    )
    timeframe_value = models.PositiveIntegerField(help_text="The number of timeframe units (e.g., 3 years).")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Objective ({self.timeframe_value} {self.timeframe_unit}) for {self.profile.username}"
