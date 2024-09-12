from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile




from django import forms

class GoalForm(forms.Form):
 
    goal = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={'placeholder': 'Enter your goal here...', 'rows': 3, 'cols': 40})
    )

   


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
  # Retrieve the User object
        
            
        return user
    
    
    
    
class GoalSimulationForm(forms.Form):
    yearly_goal = forms.ChoiceField(label='Yearly Goal')
    initial_investment = forms.ChoiceField(
        choices=[
            (0, '$0'),
            (100, '$100'),
            (1000, '$1,000'),
            (10000, '$10,000'),
            (100000, '$100,000')
        ],
        label='Initial Investment'
    )
    target_milestone = forms.ChoiceField(
        choices=[
            ('Strive to improve slightly beyond expectations', 'Strive to improve slightly beyond expectations'),
            ('Aim to surpass initial goals and achieve more', 'Aim to surpass initial goals and achieve more'),
            ('Focus on meeting the set goal without additional stretch', 'Focus on meeting the set goal without additional stretch')
        ],
        label='Target Milestone'
    )
    location = forms.ChoiceField(
        choices=[
            ('North America', 'North America'),
            ('South America', 'South America'),
            ('Europe', 'Europe'),
            ('Asia', 'Asia'),
            ('Africa', 'Africa'),
            ('Australia', 'Australia'),
            ('Antarctica', 'Antarctica')
        ],
        label='Location'
    )
    
    
class YearlyGoalForm(forms.Form):
          yearly_goal = forms.ChoiceField(label='Yearly Goal')
          
          
          


class TimeframeForm(forms.Form):
    TIMEFRAME_CHOICES = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ]

    timeframe_unit = forms.ChoiceField(choices=TIMEFRAME_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    timeframe_value = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter duration'}))
