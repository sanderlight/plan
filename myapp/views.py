from django.shortcuts import render,  get_object_or_404
from django.http import JsonResponse
from myapp.forms import  GoalForm, YearlyGoalForm
from django.shortcuts import redirect
import openai
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from openai import ChatCompletion
from googleapiclient.discovery import build
import requests
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from .models import WGoal, DGoal ,D1, M , W , D

from datetime import datetime
import calendar
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Objective, YearlyGoal, MonthlyGoal, WeeklyGoal, LongTermGoal, DailyGoal , Profile, User, Goal, UserAnalyticsData
from django.utils import timezone
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from .forms import TimeframeForm, GoalSimulationForm
import random
import uuid



GOOGLE_API_KEY = "AIzaSyCGHBqSOuxZkCwwIh52sKqP1ZAqT4WvVn8"
CSE_ID = "f5ebbb83b70c64a44"
# Set up your OpenAI API key
openai.api_key = 'sk-g-RLTZrCZeV9ya0AkIDlyCT3BlbkFJXPawA3nD87SkDvwCTc0p'




def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('index')  # Redirect to the index page after login
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})





prompts = {
    "Personal Development": "Give me an example of a personal development goal.",
    "Career Advancement": "Give me an example of a career advancement goal.",
    "Health and Wellness": "Give me an example of a health and wellness goal.",
    "Financial Planning": "Give me an example of a financial planning goal."
}

# Function to generate an example using chat completion
def generate_example(promp):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or any other chat model you prefer
        messages=[
            {"role": "system", "content": "You are an assistant that provides specific goal examples."},
            {"role": "user", "content": promp}
        ],
        max_tokens=10
    )
    example = response.choices[0].message['content'].strip()
    return example






def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile, created = Profile.objects.get_or_create(user=user)
            # Create a profile for the user
            user = User.objects.get(id=user.id)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You are now able to log in.')
            login(request, user)  # Ensure this is the correct login function
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})




from django.shortcuts import render

def year_to_day_view(request):
    # Example data for the timeline; in a real application, this could come from a database
   
  
    return render(request, 'land.html')





from datetime import date

def profile_view(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    # Fetch current date, month, and week
    current_date = date.today()
    current_month = current_date.month
    current_week = current_date.isocalendar()[1]  # ISO week number

    yearly_goals = YearlyGoal.objects.filter(profile=profile)

    # Existing data structure for Yearly, Monthly, Weekly, and Daily goals
    data = []
    for yearly_goal in yearly_goals:
        yearly_data = {
            'yearly_goal': yearly_goal,
            'monthly_goals': [],
        }
        monthly_goals = MonthlyGoal.objects.filter(yearly_goal=yearly_goal)
        for monthly_goal in monthly_goals:
            monthly_data = {
                'monthly_goal': monthly_goal,
                'weekly_goals': [],
            }
            weekly_goals = WeeklyGoal.objects.filter(monthly_goal=monthly_goal)
            for weekly_goal in weekly_goals:
                weekly_data = {
                    'weekly_goal': weekly_goal,
                    'daily_goals': DailyGoal.objects.filter(weekly_goal=weekly_goal),
                }
                monthly_data['weekly_goals'].append(weekly_data)
            yearly_data['monthly_goals'].append(monthly_data)
        data.append(yearly_data)

    # New data structure for M, W, D models
    months_data = []
    months = M.objects.filter(profile=profile)
    for month in months:
        month_data = {
            'month': month,
            'weeks': [],
        }
        weeks = W.objects.filter(month_goal=month)
        for week in weeks:
            week_data = {
                'week': week,
                'days': D.objects.filter(week_goal=week),
            }
            month_data['weeks'].append(week_data)
        months_data.append(month_data)

    # New data structure for WGoal and DGoal models
    weekly_goals_data = []
    weekly_goals = WGoal.objects.filter(profile=profile)
    for weekly_goal in weekly_goals:
        weekly_goal_data = {
            'weekly_goal': weekly_goal,
            'daily_goals': DGoal.objects.filter(weekly_goal=weekly_goal),
        }
        weekly_goals_data.append(weekly_goal_data)

    # Fetch D1 goals data
    d1_goals = D1.objects.filter(profile=user)
    
    return render(request, 'profile.html', {
        'profile': profile,
        'data': data,  # Existing goals data
        'months_data': months_data,  # New M, W, D data
        'weekly_goals_data': weekly_goals_data,  # New WGoal, DGoal data
        'd1_goals': d1_goals,  # D1 goals data
        'current_date': current_date,
        'current_month': current_month,
        'current_week': current_week,
    })



from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY  # Set your secret key


@login_required
def purchase_goal(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')
        amount = 30  # Amount in cents

        try:
            # Create a charge
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                description='Goal Purchase',
                source=token,
            )

            # Process the goal purchase
            profile = request.user.profile
            profile.goals_purchased += 1
            profile.save()

            messages.success(request, "Goal purchased successfully!")
            return redirect('profile_view')
        except stripe.error.CardError as e:
            messages.error(request, f"Payment failed: {e.user_message}")
            return redirect('subscription_payment_page')







@login_required
def subscribe_unlimited(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')

        try:
            # Create a customer and subscribe to a plan
            customer = stripe.Customer.create(
                email=request.user.email,
                source=token,
            )

            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {'price': 'your-price-id'},  # Replace with your actual price ID
                ],
                expand=['latest_invoice.payment_intent'],
            )

            # Update the user's profile to reflect the subscription
            profile = request.user.profile
            profile.subscription_type = 'Paid'
            profile.subscription_end_date = subscription.current_period_end
            profile.save()

            messages.success(request, "Subscribed to Unlimited Goals successfully!")
            return redirect('profile_view')
        except stripe.error.StripeError as e:
            messages.error(request, f"Subscription failed: {e.user_message}")
            return redirect('subscription_payment_page')
        
        
        
        
        
        
      
def index(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal_text = form.cleaned_data['goal']

            # Get or create the user's profile
            profile, created = Profile.objects.get_or_create(user=request.user)
            
            # Create a new Goal instance with the profile
            Goal.objects.create(
                profile=profile,
                goal_text=goal_text
            )

            # Redirect to the generate_long_term_goal page
            return redirect(reverse('generate_long_term_goal'))
    else:
        form = GoalForm()
    
    return render(request, 'index.html', {'form': form})



def generate_long_term_goal(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
        
        # Get the latest goal for the profile
        goal = Goal.objects.filter(profile=profile).latest('created_at')
        prompt = goal.goal_text

        if not prompt:
            return redirect('index')  # Redirect to the index page

        # Generate long-term goal using OpenAI ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )

        # Extract the generated goal from the response
        generated_goal = response.choices[0].message['content'].strip()

        # Render the goal_selection.html template with the generated goal
        return render(request, 'goal_selection.html', {'goal': generated_goal})

    except Profile.DoesNotExist:
        return redirect('index')
    except Goal.DoesNotExist:
        return redirect('index')
    except Exception as e:
        return HttpResponseBadRequest(f"Error generating goal: {str(e)}")




def generate_long_term(request):
    if request.method == 'POST':
        try:
            selected_option = request.POST.dict()  # Convert POST data to a dictionary
            option = selected_option.get('selected_option')
            tier = selected_option.get('selected_tier')
            
            if tier:
                # Construct a prompt based on the selected tier and option
                if tier == "low":
                    prompt = f"Generate a long-term goal option that can be achieved within 1-3 years based on the following input: {option}"
                elif tier == "medium":
                    prompt = f"Generate a long-term goal option that can be achieved within 3-5 years based on the following input: {option}"
                elif tier == "high":
                    prompt = f"Generate a long-term goal option that can be achieved within 5-10 years based on the following input: {option}"
                else:
                    return JsonResponse({'error': 'Invalid tier selection. Please choose a valid option.'}, status=400)
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=30
                )
                long_term_goal = response.choices[0].message['content'].strip()
            else:
                long_term_goal = f"This is a long-term goal generated based on the selected option: {option}"
            
            return render(request, 'long_term_goal.html', {'long_term_goal': long_term_goal})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return redirect('index')




def generate_goal_options(selected_goal, selected_tier):
    # Define different prompts emphasizing different aspects or dimensions of the user's input
    prompts = [
        f"What are some career-oriented goals that align with '{selected_goal}'?",
        f"Generate personal development goals related to '{selected_goal}'",
        f"Propose social impact goals inspired by '{selected_goal}'"
    ]

    goal_options = []

    # Generate goal options for each prompt
    for prompt in prompts:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Using the chat model
            messages=[
                {
                    "role": "system",
                    "content": prompt
                }
            ],
            max_tokens=50,
            n=1,  # Generate 1 option per prompt
            temperature=0.7,  # Control the diversity of generated responses
            top_p=1.0,  # Control the diversity of generated responses
            frequency_penalty=0.0,  # Control the diversity of generated responses
            presence_penalty=0.0,  # Control the diversity of generated responses
        )

        # Extract and append generated options
        goal_options.extend([choice["message"]["content"].strip() for choice in response.choices])

    return goal_options









def generate_options(request):
    if request.method == 'POST':
        selected_goal = request.POST.get('selected_goal')
        selected_tier = request.POST.get('selected_tier')
        
        # Generate diverse goal options based on the selected goal and tier
        options = generate_goal_options(selected_goal, selected_tier)
        selected_option = request.POST.get('selected_option')
        
        # Render the option selection page with the generated options
        return render(request, 'option_selection.html', {
            'options': options,
            'selected_option': selected_option,
              # Ensure 'id' is correctly passed to the template
        })
    
    # Redirect to the index page if accessed directly without a POST request
    return redirect('index')


  
  

@login_required
def generate_long_term_goals(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
        
        # Get the latest goal for the profile
        goal = Goal.objects.filter(profile=profile).latest('created_at')
        prompt = goal.goal_text

        if not prompt:
            return redirect('index')  # Redirect to the index page

        # Generate long-term goal using OpenAI ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )

        # Extract the generated goal from the response
        generated_goal = response.choices[0].message['content'].strip()

        # Render the goal_selection.html template with the generated goal
        return render(request, 'goal_selection.html', {'goal': generated_goal})

    except Profile.DoesNotExist:
        return redirect('index')
    except Goal.DoesNotExist:
        return redirect('index')
    except Exception as e:
        return HttpResponseBadRequest(f"Error generating goal: {str(e)}")


@login_required
@login_required
def generate_year_plan(request):
    """
    Generates a year plan based on a user's goal and timeframe.
    """
    if request.method == 'POST':
        # Retrieve data from the form
        long_term_goal = request.POST.get('long_term_goal')
        goal_id = request.POST.get('goal_id')
        timeframe_unit = request.POST.get('timeframe_unit')
        timeframe_value = request.POST.get('timeframe_value')

        # Ensure necessary data is provided
        if not long_term_goal or not goal_id or not timeframe_unit or not timeframe_value:
            return HttpResponseBadRequest("Incomplete form data")

        try:
            # Retrieve the goal object
            goal = Goal.objects.get(id=goal_id, profile=request.user.profile)

            # Validate that the timeframe unit is 'years'
            if timeframe_unit != 'years':
                return HttpResponseBadRequest("Only yearly plans can be generated using this view.")

            # Debugging: Print the retrieved data
            print(f"Goal: {long_term_goal}, Timeframe: {timeframe_value} {timeframe_unit}")

            # Construct the prompt for generating a plan using OpenAI
            year_plan_prompt = (
                f"What are the steps to achieve the long-term goal '{long_term_goal}' "
                f"within {timeframe_value} {timeframe_unit}?"
            )

            # Generate the year plan using OpenAI GPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": year_plan_prompt}],
                max_tokens=150  # Increased max tokens for more comprehensive output
            )

            # Extract the generated year plan
            year_plan = response.choices[0].message['content'].strip()

            if not year_plan:
                return HttpResponseBadRequest("Failed to generate a valid year plan")

            # Save multiple Yearly Goals based on timeframe value
            profile = request.user.profile
            year = timezone.now().year

            for i in range(int(timeframe_value)):
                yearly_goal = YearlyGoal.objects.create(
                    profile=profile,
                    year=year + i,
                    title=long_term_goal,
                    description=year_plan
                )

                # Debugging: Confirm the YearlyGoal creation
                print("YearlyGoal created successfully:", yearly_goal)

            # Store the generated year plan and yearly goal ID in the session
            request.session['year_plan'] = year_plan

            # Render the year_plan.html page to display the generated year plan
            return render(request, 'year_plan.html', {
                'yearly_goal': yearly_goal,
                'year_plan': year_plan
            })

        except Goal.DoesNotExist:
            return HttpResponseBadRequest("Goal not found")
        except Exception as e:
            print(f"Error generating year plan: {e}")
            return HttpResponseBadRequest("Failed to generate year plan")

    # Handle non-POST requests
    return HttpResponseBadRequest("Invalid request method. Use POST to submit data.")


def generate_month_to_month_plans_from_year_plan(year_plan):
    """
    Generates month-to-month plans from a year plan using OpenAI GPT-4.
    """
    month_to_month_plans = []
    for month in range(1, 13):
        month_prompt = f"What are the steps to achieve the long-term goal '{year_plan}' within month {month}?"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": month_prompt}],
            max_tokens=50
        )
        month_plan = response.choices[0].message['content'].strip()
        month_to_month_plans.append((month, month_plan))
    return month_to_month_plans

def generate_month_to_month_plans_view(request, id):
    if request.method == 'POST':
        # Extract data from POST request
        year_plan = request.POST.get('year_plan')
        yearly_goal_id = request.POST.get('yearly_goal')

        # Debugging: Print received year_plan and yearly_goal_id
        print("Received year_plan:", year_plan)
        print("Received yearly_goal_id:", yearly_goal_id)

        if not year_plan or not yearly_goal_id:
            # Debugging: Print which part is missing
            if not year_plan:
                print("Year plan is missing")
            if not yearly_goal_id:
                print("Yearly goal ID is missing")
            
            return HttpResponseBadRequest("Missing year plan or yearly goal")

        # Retrieve the YearlyGoal object
        try:
            yearly_goal = YearlyGoal.objects.get(id=yearly_goal_id)
        except YearlyGoal.DoesNotExist:
            return HttpResponseBadRequest("Yearly goal not found")

        # Generate month-to-month plans from the year plan
        month_to_month_plans = generate_month_to_month_plans_from_year_plan(year_plan)
        current_month = timezone.now().month
        month_names = [calendar.month_name[(current_month + i - 1) % 12 + 1] for i in range(12)]

        month_to_month_plans_named = []
        for i, (month_name, month_plan) in enumerate(zip(month_names, month_to_month_plans)):
            # Check if a MonthlyGoal already exists for this month
            monthly_goal, created = MonthlyGoal.objects.get_or_create(
                yearly_goal=yearly_goal,
                month=(current_month + i - 1) % 12 + 1,
                defaults={'description': month_plan[1]}
            )
            month_to_month_plans_named.append((month_name, monthly_goal.id, monthly_goal.description))
        
        # Store the month-to-month plans and year plan in the session
        request.session['month_to_month_plans'] = month_to_month_plans_named
        request.session['year_plan'] = year_plan  # Store the year plan for reference

        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        return render(request, 'month.html', {
            'month_to_month_plans': month_to_month_plans_named,
            'timestamp': timestamp,
            'id': id
        })

    elif request.method == 'GET':
        return HttpResponse("This view expects a POST request to submit data.")
    
    return HttpResponseBadRequest("Invalid request method. Use POST to submit data.")




def generate_ai_content(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating content: {e}")
        return None
    
    
    
    
from django.shortcuts import render, redirect



  

TimeframeForm
from django.shortcuts import render, redirect




@login_required
def setup_goal_view(request):
    if request.method == 'POST':
        
        long_term_goal = request.POST.get('long_term_goal') or request.session.get('long_term_goal')
        
        print(f"Long-term goal retrieved: {long_term_goal}")  # Debugging line
       
        
        
        form = TimeframeForm(request.POST)
        
        if form.is_valid():
            timeframe_unit = form.cleaned_data['timeframe_unit']
            timeframe_value = form.cleaned_data['timeframe_value']
            long_term_goal = request.POST.get('long_term_goal')
            # Retrieve 'long_term_goal' directly from POST data
            print(f"Long-term goal retrieved: {long_term_goal}")  # Debugging line


            if not long_term_goal:
                return JsonResponse({'error': 'Long-term goal not provided'}, status=400)

            # Save the new objective instance
            new_objective = Objective(
                profile=request.user.profile, 
                timeframe_unit=timeframe_unit,
                timeframe_value=timeframe_value
            )
            new_objective.save()

            # Store 'long_term_goal' in the session for later use
            request.session['long_term_goal '] = long_term_goal

            # Define determine_redirect_url function if not already
            def determine_redirect_url(timeframe_unit):
                if timeframe_unit == 'days':
                    return reverse('generate_day_plan')
                elif timeframe_unit == 'weeks':
                    return reverse('generate_week_plan')
                elif timeframe_unit == 'months':
                    return reverse('generate_month_plan')
                elif timeframe_unit == 'years':
                    return reverse('generate_year_plan')
                else:
                    return reverse('default_page')

            # Use the determine_redirect_url function
            redirect_url = determine_redirect_url(timeframe_unit)
            return redirect(redirect_url)
    else:
        form = TimeframeForm()

    return render(request, 'setup_goal.html', {'form': form})









def generate_month_plan(request):
    if request.method == 'POST':
        long_term_goal = request.POST.get('long_term_goal') or request.session.get('long_term_goal')
        
        
        print(f"Long-term goal retrieved: {long_term_goal}")  # Debugging line

        try:
            # Retrieve timeframe_unit and timeframe_value from POST data
            timeframe_unit = request.POST.get('timeframe_unit')
            timeframe_value = request.POST.get('timeframe_value')
           

            if not long_term_goal:
                return JsonResponse({'error': 'Long-term goal not provided or missing from session'}, status=400)

            if not timeframe_unit or not timeframe_value:
                return JsonResponse({'error': 'Timeframe unit or value not provided'}, status=400)

            # Convert timeframe_value to an integer
            try:
                timeframe_value = int(timeframe_value)
            except ValueError:
                return JsonResponse({'error': 'Invalid timeframe value'}, status=400)

            # Retrieve the profile of the currently logged-in user
            profile = get_object_or_404(Profile, user=request.user)

            # Determine the number of months based on the timeframe unit
            num_months = timeframe_value if timeframe_unit == 'months' else 12  # Default to 12 months if not 'months'

            # Generate month-to-month plans using OpenAI GPT-4
            month_to_month_plans = []
            for month in range(1, num_months + 1):
                month_prompt = f"What are the steps to achieve the long-term goal '{long_term_goal}' within month {month}?"
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": month_prompt}],
                    max_tokens=50
                )
                month_plan = response.choices[0].message['content'].strip()

                # Create a new M instance (MonthlyGoal)
                monthly_goal = M.objects.create(
                    month_number=month,
                    month_description=month_plan,
                    profile=profile  # Save the profile of the currently logged-in user
                )
                month_to_month_plans.append(monthly_goal)
                

            # Render the month plan template with the generated month-to-month plans
            return render(request, 'months.html', {'month_to_month_plans': month_to_month_plans})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)





@login_required
def generate_week_plan_from_month(request, id):
    """
    Generates week-to-week plans from a month plan.
    """
    if request.method == 'POST':
        try:
            # Retrieve the month ID from POST data or URL
            month_id = request.POST.get('month_id') or id
            month_plan = get_object_or_404(M, id=month_id)
            
            # Number of weeks to generate plans for (e.g., assume 4 weeks in a month)
            num_weeks = 4

            # Generate week-to-week plans using OpenAI GPT-4
            week_to_week_plans = []
            for week in range(1, num_weeks + 1):
                week_prompt = f"What are the steps to achieve the monthly goal '{month_plan.month_description}' for week {week}?"
                
                # Get response from OpenAI GPT-4
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": week_prompt}],
                    max_tokens=50
                )
                
                week_plan = response.choices[0].message['content'].strip()

                # Create a new weekly goal
                weekly_goal = W.objects.create(
                    profile=month_plan.profile,  # Ensure the profile is correct
                    month_goal=month_plan,       # Correct field name
                                    # Set as needed
                    week_number=week,
                    week_description=week_plan  # Use generated text for the description
                )
                
                weekly_goal.save()

                # Append the generated week plan to the list
                week_to_week_plans.append(weekly_goal)

            # Render the week plan template with the generated week-to-week plans
            return render(request, 'month-to-week.html', {'week_to_week_plans': week_to_week_plans, 'monthly_goal': month_plan})

        except M.DoesNotExist:
            return JsonResponse({'error': 'Monthly goal not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    
    
from django.db import IntegrityError  # Import IntegrityError from Django
from dateutil.parser import parse
    

@login_required
def generate_day_plan_from_month(request, id):
    """
    Generates day-to-day plans from the weekly goals derived from a specific monthly goal.
    """
    try:
        # Retrieve the MonthlyGoal instance using the month_goal_id
        month_id = request.POST.get('month_id') or id
        monthly_goal = get_object_or_404(M, id=month_id)
        
        # Ensure the profile exists and is set correctly
        if not monthly_goal.profile:
            return JsonResponse({'error': 'Profile associated with monthly goal is missing'}, status=400)
        
        # Fetch all WeeklyGoals associated with the MonthlyGoal
        weekly_goals = W.objects.filter(month_goal=monthly_goal).order_by('week_number')
        
        # Initialize an empty list to store the day-to-day plans
        day_to_day_plans = []

        # Generate day-to-day plans for each weekly goal within the month
        for weekly_goal in weekly_goals:
            # Ensure the week_goal and profile foreign keys are valid
            if not weekly_goal.profile or not weekly_goal.month_goal:
                continue  # Skip if invalid foreign key

            # Assuming each week has 7 days
            for day in range(1, 8):  # Generate daily goals for each day of the week
                day_prompt = (
                    f"Based on the weekly goal '{weekly_goal.week_description}', "
                    f"what are the steps to achieve this on day {day} of week {weekly_goal.week_number}?"
                )

                try:
                    # Generate day plan using GPT-4 with a timeout
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": day_prompt}],
                        max_tokens=50,
                        timeout=10  # Set timeout to 10 seconds
                    )
                    day_plan = response.choices[0].message['content'].strip()

                    # Create or retrieve DailyGoal instance
                    daily_goal, created = D.objects.get_or_create(
                        week_goal=weekly_goal,
                        profile=monthly_goal.profile, 
                        day_number=day,
                        defaults={'day_description': day_plan}
                    )
                    
                    # Append to the list of day-to-day plans
                    day_to_day_plans.append((weekly_goal, day, daily_goal))

                except Exception as api_error:
                    print(f"Error with OpenAI API call: {str(api_error)}")
                    continue  # Skip to the next day if API call fails

        # Render the template with the generated day-to-day plans
        return render(request, 'month-to-day.html', {
            'monthly_goal': monthly_goal,
            'day_to_day_plans': day_to_day_plans
        })

    except M.DoesNotExist:
        return JsonResponse({'error': 'Monthly goal not found'}, status=404)
    except IntegrityError as e:
        return JsonResponse({'error': 'Integrity error: possible foreign key constraint issue'}, status=400)
    except Exception as e:
        return HttpResponseBadRequest(f"Error generating day plan: {str(e)}")

    


    
    


@login_required
def generate_day_plan(request):
    """
    Generates day-to-day plans based on user input and goal.
    """
    if request.method == 'POST':
        # Retrieve form data
             # Retrieve long_term_goal from session
        long_term_goal = request.session.get('long_term_goal')
        timeframe_unit = request.POST.get('timeframe_unit')
        timeframe_value = request.POST.get('timeframe_value')

        
        try:
            # Determine the number of days based on the timeframe
            num_days = int(timeframe_value) if timeframe_unit == 'days' else 7  # Default to 7 days if not 'days'

            # Generate day-to-day plans using OpenAI GPT-4
            day_to_day_plans = []
            for day in range(1, num_days + 1):
                day_prompt = (
                    f"What are the steps to achieve the goal '{long_term_goal}' "
                    f"for day {day}?"
                )
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": day_prompt}],
                    max_tokens=150  # Increased max tokens for more comprehensive output
                )
                day_plan = response.choices[0].message['content'].strip()

                if not day_plan:
                    return HttpResponseBadRequest("Failed to generate a valid day plan")

                # Create a new D1 instance with the correct profile
                daily_goal = D1.objects.create(
                    profile=request.user,  # Correctly set the profile
                    title=f"Day {day} Plan",
                    description=day_plan,
                    date=timezone.now().date() + timedelta(days=day - 1),  # Set the date for each day
                    start_date=timezone.now().date()  # Ensure start_date is set if required
                )

                # Append the generated day plan to the list
                day_to_day_plans.append(daily_goal)

            # Render the day plan template with the generated day-to-day plans
            return render(request, 'day_goal.html', {
                'day_to_day_plans': day_to_day_plans,
                'goal': long_term_goal
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Handle non-POST requests
    return HttpResponseBadRequest("Invalid request method. Use POST to submit data.")

import datetime
# View to Generate Week-to-Week Plans
@login_required
def generate_week_to_week_plan(request):
    """
    Generates week-to-week plans based on user input and goal.
    """
    if request.method == 'POST':
        # Retrieve data from the form and session
        long_term_goal = request.session.get('long_term_goal', '')
        timeframe_unit = request.POST.get('timeframe_unit')
        timeframe_value = request.POST.get('timeframe_value')

        # Ensure the user has a profile
        profile = request.user.profile  # Assuming `Profile` is related to `User` via a OneToOneField

        try:
            # Determine the number of weeks based on the timeframe
            num_weeks = int(timeframe_value) if timeframe_unit == 'weeks' else 4  # Default to 4 weeks if not 'weeks'

            # Generate week-to-week plans using OpenAI GPT-4
            week_to_week_plans = []
            for week in range(1, num_weeks + 1):
                week_prompt = (
                    f"What are the steps to achieve the goal '{long_term_goal}' "
                    f"for week {week}?"
                )
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": week_prompt}],
                    max_tokens=150  # Increased max tokens for more comprehensive output
                )
                week_plan = response.choices[0].message['content'].strip()

                if not week_plan:
                    return HttpResponseBadRequest("Failed to generate a valid week plan")

                # Create a new WeeklyGoal instance with the required profile field
                weekly_goal = WGoal.objects.create(
                    week_number=week,
                    goal_text=long_term_goal,
                    week_description=week_plan,
                    profile=profile,  # Make sure to set the profile
                    start_date=datetime.date.today()  # Ensure start_date is set if required
                )
                week_to_week_plans.append(weekly_goal)

            # Render the week plan template with the generated week-to-week plans
            return render(request, 'week_goal.html', {
                'week_to_week_plans': week_to_week_plans,
                'goal_text': long_term_goal
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Handle non-POST requests
    return HttpResponseBadRequest("Invalid request method. Use POST to submit data.")


def generate_week_to_day_plan(request, week_goal_id):
    """
    View to generate day-to-day plans for a specific week goal.
    """
    try:
        # Retrieve the WeeklyGoal instance using the provided week_goal_id
        weekly_goal = get_object_or_404(WGoal, id=week_goal_id)
        day_to_day_plans = []

        # Ensure the user has a profile
        profile = weekly_goal.profile  # Assuming WGoal has a profile field

        # Define the number of days (example: 7 days for simplicity)
        num_days = 7

        # Generate day-to-day plans using OpenAI GPT-4 or other logic
        for day in range(1, num_days + 1):
            day_prompt = f"What are the steps to achieve the goal '{weekly_goal.goal_text}' for day {day} of week {weekly_goal.week_number}?"
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": day_prompt}],
                max_tokens=50
            )
            day_plan = response.choices[0].message['content'].strip()

            # Create a new DailyGoal instance with the required fields
            daily_goal = DGoal.objects.create(
                weekly_goal=weekly_goal,
                day_number=day,
                day_description=day_plan,
                profile=profile,  # Make sure to set the profile
                start_date=datetime.date.today()  # Set start_date
            )
            day_to_day_plans.append(daily_goal)

        return render(request, 'week_to_day.html', {'day_to_day_plans': day_to_day_plans, 'weekly_goal': weekly_goal})

    except WGoal.DoesNotExist:
        return JsonResponse({'error': 'Weekly goal not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)





    
    

    
def generate_week_to_week_plans_view(request, id):
    try:
        # Retrieve month_to_month_plans from the session
        month_to_month_plans = request.session.get('month_to_month_plans')

        # Debugging: Print the content of month_to_month_plans
        print("Month to month plans:", month_to_month_plans)

        # Check if month_to_month_plans is present
        if not month_to_month_plans:
            return redirect('generate_month_to_month_plans_view')

        week_to_week_plans_by_month = []

        # Iterate over each month plan
        for i, month_plan in enumerate(month_to_month_plans):
            # Debugging: Print the content of the current month_plan
            print("Processing month_plan:", month_plan)

            # Ensure the month_plan is a tuple or list with exactly three values
            if not isinstance(month_plan, (tuple, list)) or len(month_plan) != 3:
                raise ValueError(f"Invalid month_plan format: {month_plan}")

            month_name, month_plan_id, month_plan_description = month_plan

            # Ensure month_plan_id is a valid number
            if not isinstance(month_plan_id, int):
                raise ValueError(f"Invalid month_plan_id: {month_plan_id}")

            # Get the MonthlyGoal instance using the ID
            monthly_goal = MonthlyGoal.objects.get(id=month_plan_id)

            # Generate week-to-week plans
            week_plans = generate_week_to_week_plans_from_month_plan(monthly_goal, i * 4 + 1)
            week_to_week_plans_by_month.append((month_name, week_plans))

        print("Week to week plans by month:", week_to_week_plans_by_month)

        return render(request, 'week.html', {'week_to_week_plans_by_month': week_to_week_plans_by_month, 'id': id})
    except MonthlyGoal.DoesNotExist:
        return JsonResponse({'error': 'Monthly goal not found'}, status=404)
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    
    
    
    
    
    
    
    
    
    
import time

def generate_week_to_week_plans_from_month_plan(monthly_goal, start_week, max_retries=3, retry_delay=5):
    """
    Generates week-to-week plans from a single month plan and saves them as WeeklyGoal instances.
    """
    if not isinstance(monthly_goal, MonthlyGoal):
        raise ValueError("The monthly_goal parameter must be a MonthlyGoal instance")

    week_to_week_plans = []
    month_plan = monthly_goal.description
    month_name = calendar.month_name[monthly_goal.month]  # Assuming 'month' is an integer field

    # Retrieve the associated yearly_goal
    yearly_goal = monthly_goal.yearly_goal

    for week in range(start_week, start_week + 4):  # Assuming 4 weeks per month
        week_prompt = f"What are the steps to achieve the month goal '{month_plan}' for {month_name} in week {week - start_week + 1}?"
        print(f"Generating plan for: {week_prompt}")  # Debugging: Print the prompt

        retries = 0
        while retries < max_retries:
            try:
                response = ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": week_prompt}],
                    max_tokens=50  # Increased max_tokens for more detailed responses
                )
                week_plan = response.choices[0].message['content'].strip()

                if not week_plan:
                    raise ValueError("Received empty week plan from OpenAI API")

                # Check if a WeeklyGoal already exists for the given monthly_goal and week
                weekly_goal, created = WeeklyGoal.objects.update_or_create(
                    monthly_goal=monthly_goal,
                    yearly_goal=yearly_goal,
                    week=week,
                    defaults={'description': week_plan}
                )

                if not weekly_goal.id:
                    raise ValueError("Failed to save the weekly goal to the database")

                week_to_week_plans.append((f"Week {week - start_week + 1}", week_plan))

                # Debugging: Confirm that the weekly goal was saved
                print(f"{'Created' if created else 'Updated'} weekly goal: {weekly_goal.description}")
                break
            except Exception as e:
                if "connection was forcibly closed by the remote host" in str(e):
                    retries += 1
                    print(f"Connection error: {str(e)}. Retrying {retries}/{max_retries}...")
                    time.sleep(retry_delay)
                else:
                    print(f"Error generating or saving week plan for week {week - start_week + 1}: {str(e)}")
                    raise

    return week_to_week_plans






def daily_goal_view(request, id):
    user = request.user
    week_plan_description = request.POST.get('week_plan_description')
    current_date = timezone.now().date()
    daily_goals = None

    try:
        # Retrieve the YearlyGoal instance using the ID from the URL
        yearly_goal = get_object_or_404(YearlyGoal, id=id)
        print(f"Yearly Goal ID from DB: {yearly_goal.id}")

        if request.method == 'POST':
            # Generate daily goals based on the week plan description
            profile = Profile.objects.get(user=user)
            result_message, daily_goal = generate_daily_goal_from_week_plan(
                profile,
                yearly_goal,
                week_plan_description,
                current_date
            )

            if daily_goal:
                # Redirect to the same view with the yearly goal ID after generating the daily goal
                return redirect('daily_goals', id=yearly_goal.id)
            else:
                return render(request, 'daily_goal.html', {
                    'error': 'No new daily goals were generated.',
                    'yearly_goal': yearly_goal,
                    'daily_goals': daily_goals
                })
        else:
            # For GET requests, just display existing daily goals
            daily_goals = DailyGoal.objects.filter(yearly_goal=yearly_goal)
            print(f"Daily Goals Count: {daily_goals.count()}")

            if not daily_goals:
                return render(request, 'daily_goal.html', {
                    'error': 'No daily goals available for this yearly goal.',
                    'yearly_goal': yearly_goal
                })

            return render(request, 'daily_goal.html', {
                'yearly_goal': yearly_goal,
                'daily_goals': daily_goals
            })

    except Profile.DoesNotExist:
        return render(request, 'daily_goal.html', {'error': 'Profile does not exist for the current user.'})
    except YearlyGoal.DoesNotExist:
        return render(request, 'daily_goal.html', {'error': 'Yearly goal does not exist for the given ID.'})
    except Exception as e:
        return render(request, 'daily_goal.html', {'error': str(e), 'yearly_goal': yearly_goal, 'daily_goals': daily_goals})


def calculate_week_sequence(yearly_goal, current_date):
    # Use the creation date of the yearly goal as the start date
    yearly_goal_start_date = yearly_goal.created_at.date()  # Ensure 'created_at' is a datetime field
    delta = current_date - yearly_goal_start_date
    return (delta.days // 7) + 1

def generate_daily_goal_from_week_plan(profile, yearly_goal, week_plan_description, current_date, weekly_goal_id=None):
    try:
        # Ensure that the MonthlyGoal exists or create it if not
        monthly_goal, created = MonthlyGoal.objects.get_or_create(
            yearly_goal=yearly_goal,
            month=current_date.month,
            defaults={'description': ''}
        )

        week_number = calculate_week_sequence(yearly_goal, current_date)  # Use the updated function

        # Try to get the WeeklyGoal by ID if provided
        if weekly_goal_id:
            weekly_goal = WeeklyGoal.objects.filter(id=weekly_goal_id).first()
        else:
            # Try to get an existing WeeklyGoal by attributes
            weekly_goal = WeeklyGoal.objects.filter(
                yearly_goal=yearly_goal,
                monthly_goal=monthly_goal,
                week=week_number
            ).first()

        if weekly_goal is None:
            # Handle the case where no WeeklyGoal is found
            print(f"No existing WeeklyGoal found for yearly_goal={yearly_goal.id}, monthly_goal={monthly_goal.id}, week={week_number}, id={weekly_goal_id}")
            return "No WeeklyGoal found for the given parameters.", None

        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=6)

        existing_daily_goals = DailyGoal.objects.filter(
            profile=profile,
            weekly_goal=weekly_goal,
            date__range=[week_start, week_end]
        ).values_list('description', flat=True)

        is_unique = False
        new_goal_description = ""
        attempts = 0
        max_attempts = 5

        while not is_unique and attempts < max_attempts:
            attempts += 1

            day_prompt = f"What are the steps to achieve the week goal '{week_plan_description}' on {current_date.strftime('%A')}?"
            response = ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": day_prompt}],
                max_tokens=50
            )
            day_plan = response.choices[0].message['content'].strip()

            additional_content = "Additional content related to the week plan description."
            new_goal_description = f"{day_plan} {additional_content}"

            is_unique = new_goal_description not in existing_daily_goals

            if is_unique:
                # Save the new daily goal
                daily_goal = DailyGoal.objects.create(
                    profile=profile,
                    weekly_goal=weekly_goal,
                    title=f"Daily Goal for {current_date.strftime('%A')}",
                    description=new_goal_description,
                    date=current_date,
                    monthly_goal=monthly_goal,
                    yearly_goal=yearly_goal
                )
                return f"Daily goals for the week starting {week_start.strftime('%Y-%m-%d')} have been generated.", daily_goal
            else:
                print(f"Attempt {attempts}: Generated goal not unique.")

        raise Exception("Unable to generate a unique goal after several attempts.")

    except Exception as e:
        raise Exception(f"Error generating daily goal: {str(e)}")
    
    
    
    import parser
    
    


@login_required
def daily_goal_detail_view(request):
    user = request.user
    user_profile = get_object_or_404(Profile, user=user)

    # Get the date from query parameters or default to today's date
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = parse_date(date_str)
        except ValueError:
            if request.is_ajax():
                return JsonResponse({'error': 'Invalid date format.'}, status=400)
            return render(request, 'day.html', {'error': 'Invalid date format.'})
    else:
        latest_goal = DailyGoal.objects.filter(profile=user_profile).latest('date') if DailyGoal.objects.filter(profile=user_profile).exists() else None
        target_date = latest_goal.date if latest_goal else datetime.today().date()

    # Retrieve the selected yearly goal from the query parameters
    yearly_goal_id = request.GET.get('yearly_goal_id')
    if yearly_goal_id:
        yearly_goal = get_object_or_404(YearlyGoal, id=yearly_goal_id, profile=user_profile)
        yearly_goals = YearlyGoal.objects.filter(profile=user_profile, id=yearly_goal_id)
    else:
        yearly_goals = YearlyGoal.objects.filter(profile=user_profile, year=target_date.year)
    
    if not yearly_goals.exists():
        if request.is_ajax():
            return JsonResponse({'error': 'No yearly goals found for the current year.'}, status=404)
        return render(request, 'day.html', {'error': 'No yearly goals found for the current year.'})

    # Generate daily goals for the selected yearly goal
    today = datetime.today().date()
    current_date = target_date
    while current_date <= today:
        daily_goal = DailyGoal.objects.filter(profile=user_profile, yearly_goal__in=yearly_goals, date=current_date).first()
        if not daily_goal:
            for yearly_goal in yearly_goals:
                # Attempt to retrieve the correct weekly plan description
                week_plan = WeeklyGoal.objects.filter(yearly_goal=yearly_goal).first()
                if week_plan:
                    week_plan_description = week_plan.description
                else:
                    week_plan_description = "Default week plan description"
                
                message, new_daily_goal = generate_daily_goal_from_week_plan(
                    profile=user_profile,
                    yearly_goal=yearly_goal,
                    week_plan_description=week_plan_description,  # Use the correct description
                    current_date=current_date
                )
                if new_daily_goal:
                    # Handle the newly created daily goal if needed
                    pass
        current_date += timedelta(days=1)

    # Retrieve the daily goals for the target date and selected yearly goal
    daily_goals = DailyGoal.objects.filter(profile=user_profile, yearly_goal__in=yearly_goals, date=target_date)
    daily_goals_data = [{
        'id': goal.id,
        'title': goal.title,
        'description': goal.description,
        'date': goal.date.strftime('%Y-%m-%d'),
        'completed': goal.completed
    } for goal in daily_goals]

    if request.is_ajax():
        return JsonResponse({'daily_goals': daily_goals_data})

    return render(request, 'day.html', {
        'daily_goal': daily_goals.first() if daily_goals.exists() else None,
        'daily_goals': daily_goals,
        'profile': user_profile,
        'yearly_goals': yearly_goals,
    })




def get_yearly_goal_dates_view(request):
    yearly_goal_id = request.GET.get('yearly_goal_id')
    if not yearly_goal_id:
        return JsonResponse({'error': 'Yearly goal ID not provided.'}, status=400)

    try:
        # Retrieve the yearly goal and associated daily goals
        yearly_goal = YearlyGoal.objects.get(id=yearly_goal_id)
        daily_goals = DailyGoal.objects.filter(yearly_goal=yearly_goal)

        # Extract the unique dates of the daily goals
        goal_dates = list(daily_goals.values_list('date', flat=True).distinct())

        return JsonResponse({'goal_dates': goal_dates}, status=200)
    except YearlyGoal.DoesNotExist:
        return JsonResponse({'error': 'Yearly goal not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)









def get_yearly_goals(request):
    profile = Profile.objects.get(user=request.user)
    yearly_goals = YearlyGoal.objects.filter(profile=profile)

    data = [{
        'id': goal.id,
        'title': goal.title,
        'description': goal.description
    } for goal in yearly_goals]

    return JsonResponse(data, safe=False)


def get_yearly_goal_details(request):
    goal_id = request.GET.get('id')
    try:
        goal = YearlyGoal.objects.get(id=goal_id)
        data = {
            'title': goal.title,
            'description': goal.description
        }
        return JsonResponse(data)
    except YearlyGoal.DoesNotExist:
        return JsonResponse({'error': 'Yearly goal not found'}, status=404)


def get_monthly_goals(request):
    yearly_goal_id = request.GET.get('yearly_goal_id')
    if not yearly_goal_id:
        return JsonResponse({'error': 'Yearly goal ID is required'}, status=400)

    yearly_goal = YearlyGoal.objects.get(id=yearly_goal_id)
    monthly_goals = yearly_goal.monthlygoal_set.all()

    data = [{
        'id': mgoal.id,
        'month': mgoal.month,
        'description': mgoal.description
    } for mgoal in monthly_goals]

    return JsonResponse(data, safe=False)

def get_monthly_goal_details(request):
    goal_id = request.GET.get('id')
    try:
        goal = MonthlyGoal.objects.get(id=goal_id)
        data = {
            'title': goal.month,
            'description': goal.description
        }
        return JsonResponse(data)
    except MonthlyGoal.DoesNotExist:
        return JsonResponse({'error': 'Monthly goal not found'}, status=404)

def get_weekly_goals(request):
    monthly_goal_id = request.GET.get('monthly_goal_id')
    if not monthly_goal_id:
        return JsonResponse({'error': 'Monthly goal ID is required'}, status=400)

    monthly_goal = MonthlyGoal.objects.get(id=monthly_goal_id)
    weekly_goals = monthly_goal.weeklygoal_set.all()

    data = [{
        'id': wgoal.id,
        'week': wgoal.week,
        'description': wgoal.description
    } for wgoal in weekly_goals]

    return JsonResponse(data, safe=False)

def get_weekly_goal_details(request):
    goal_id = request.GET.get('id')
    try:
        goal = WeeklyGoal.objects.get(id=goal_id)
        data = {
            'title': f"Week {goal.week}",
            'description': goal.description
        }
        return JsonResponse(data)
    except WeeklyGoal.DoesNotExist:
        return JsonResponse({'error': 'Weekly goal not found'}, status=404)

def get_daily_goal(request):
    weekly_goal_id = request.GET.get('weekly_goal_id')
    if not weekly_goal_id:
        return JsonResponse({'error': 'Weekly goal ID is required'}, status=400)

    weekly_goal = WeeklyGoal.objects.get(id=weekly_goal_id)
    daily_goals = weekly_goal.dailygoal_set.all()

    data = [{
        'id': dgoal.id,
        'date': str(dgoal.date),
        'description': dgoal.description
    } for dgoal in daily_goals]

    return JsonResponse(data, safe=False)

def get_daily_goal_details(request):
    daily_goal_id = request.GET.get('id')
    try:
        daily_goal = DailyGoal.objects.get(id=daily_goal_id)
        response_data = {
            'dailyGoal': {
                'title': daily_goal.title,
                'description': daily_goal.description,
                'date': daily_goal.date,
            }
        }
        return JsonResponse(response_data)
    except DailyGoal.DoesNotExist:
        return JsonResponse({'error': 'Daily goal not found'}, status=404)
    
    


def get_monthly_goals(request):
    profile_id = request.GET.get('profile_id')
    monthly_goals = M.objects.filter(profile_id=profile_id)
    data = [{'id': goal.id, 'month_number': goal.month_number, 'month_description': goal.month_description} for goal in monthly_goals]
    return JsonResponse(data, safe=False)

def get_weekly_goals(request):
    month_id = request.GET.get('month_id')
    weekly_goals = W.objects.filter(month_goal_id=month_id)
    data = [{'id': goal.id, 'week_number': goal.week_number, 'week_description': goal.week_description} for goal in weekly_goals]
    return JsonResponse(data, safe=False)

def get_daily_goals(request):
    week_id = request.GET.get('week_id')
    daily_goals = D.objects.filter(week_goal_id=week_id)
    data = [{'id': goal.id, 'day_number': goal.day_number, 'day_description': goal.day_description} for goal in daily_goals]
    return JsonResponse(data, safe=False)

def get_wgoal_details(request):
    wgoal_id = request.GET.get('wgoal_id')
    wgoal = get_object_or_404(WGoal, id=wgoal_id)
    data = {
        'id': wgoal.id,
        'goal_text': wgoal.goal_text,
        'week_number': wgoal.week_number,
        'week_description': wgoal.week_description,
        'start_date': wgoal.start_date,
    }
    return JsonResponse(data)

def get_dgoal_details(request):
    dgoal_id = request.GET.get('dgoal_id')
    dgoal = get_object_or_404(DGoal, id=dgoal_id)
    data = {
        'id': dgoal.id,
        'day_number': dgoal.day_number,
        'day_description': dgoal.day_description,
        'start_date': dgoal.start_date,
    }
    return JsonResponse(data)

def get_d1_goals(request):
    profile_id = request.GET.get('profile_id')
    d1_goals = D1.objects.filter(profile_id=profile_id)
    data = [{'id': goal.id, 'title': goal.title, 'description': goal.description, 'date': goal.date, 'completed': goal.completed} for goal in d1_goals]
    return JsonResponse(data, safe=False)



  
    
    
    
    


@login_required

def generate_goals(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        user = request.user
        profile = Profile.objects.get(user=user)

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            generate_daily_goal_from_week_plan(profile, "Week Plan Description", target_date)
            return JsonResponse({'message': 'Goals generated successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def get_daily_goals(request):
    user_profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = YearlyGoalForm(request.POST)
        # Populate choices for the form field
        yearly_goals = YearlyGoal.objects.filter(profile=user_profile)
        form.fields['yearly_goal'].choices = [(goal.id, goal.title) for goal in yearly_goals]

        if form.is_valid():
            yearly_goal_id = form.cleaned_data['yearly_goal']
            yearly_goal = get_object_or_404(YearlyGoal, id=yearly_goal_id, profile=user_profile)
            
            # Retrieve daily goals for the selected yearly goal
            daily_goals = DailyGoal.objects.filter(yearly_goal=yearly_goal).values('title', 'date', 'completed')
            return JsonResponse({'daily_goals': list(daily_goals)})
        
        return JsonResponse({'error': 'Form is not valid.'}, status=400)
    
    else:
        # Handle GET request, e.g., render form or provide default data
        form = YearlyGoalForm()
        yearly_goals = YearlyGoal.objects.filter(profile=user_profile)
        form.fields['yearly_goal'].choices = [(goal.id, goal.title) for goal in yearly_goals]

        return render(request, 'select_yearly_goal.html', {'form': form})
    
    








@login_required
def update_daily_goal_status_view(request, id):
    user_profile = get_object_or_404(Profile, user=request.user)
    daily_goal = get_object_or_404(DailyGoal, profile=user_profile, id=id)
    
    if request.method == 'POST':
        completed = request.POST.get('completed') == 'true'
        daily_goal.completed = completed
        daily_goal.save()

        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)




from .utils import run_simulation


def goal_simulation(request):
    profile = request.user.profile
    yearly_goals = YearlyGoal.objects.filter(profile=profile)
    
    if request.method == 'POST':
        form = GoalSimulationForm(request.POST)
        form.fields['yearly_goal'].choices = [(goal.id, goal.title) for goal in yearly_goals]
        
        if form.is_valid():
            yearly_goal_id = form.cleaned_data['yearly_goal']
            initial_investment = form.cleaned_data['initial_investment']
            target_milestone = form.cleaned_data['target_milestone']
            location = form.cleaned_data['location']
            
            # Retrieve the selected yearly goal
            yearly_goal = YearlyGoal.objects.get(id=yearly_goal_id)
            
            # Run the simulation
            probability_percentage, result_summary = run_simulation(yearly_goal, initial_investment, target_milestone, location)
            
            # Pass the results to the context
            context = {
                'form': form,
                'probability_percentage': probability_percentage,
                'result_summary': result_summary,
            }
            
            return render(request, 'goal_simulation.html', context)
    
    else:
        form = GoalSimulationForm()
        form.fields['yearly_goal'].choices = [(goal.id, goal.title) for goal in yearly_goals]

    context = {
        'form': form,
    }
    
    return render(request, 'goal_simulation.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Profile, DailyGoal, YearlyGoal

def analytics_view(request):
    # Get the user's profile
    user_profile = get_object_or_404(Profile, user=request.user)
    
    # Retrieve daily goals associated with the user's profile
    daily_goals = DailyGoal.objects.filter(profile=user_profile)
    
    # Retrieve all yearly goals to populate the dropdown
    yearly_goals = YearlyGoal.objects.filter(profile=user_profile)  # Adjust if needed
    
    # Pass the daily goals and yearly goals to the template
    return render(request, 'analytics.html', {'daily_goals': daily_goals, 'yearly_goals': yearly_goals})










@login_required
def analytics_data_view(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    
    # Retrieve the selected yearly goal ID from the request
    yearly_goal_id = request.GET.get('yearly_goal_id')
    
    # Fetch daily goals filtered by the selected yearly goal if provided
    if yearly_goal_id:
        daily_goals = DailyGoal.objects.filter(profile=user_profile, yearly_goal_id=yearly_goal_id)
    else:
        daily_goals = DailyGoal.objects.filter(profile=user_profile)
    
    # Initialize analytics data
    goalProgress = 0
    daysLeft = 0
    goalStatus = 'red'
    todayCompleted = False
    
    # Ensure there are daily goals to work with
    if daily_goals.exists():
        # Calculate the number of days since the start of the goal
        start_date = daily_goals.earliest('date').date
        end_date = start_date + timedelta(days=365)  # Assumes a 1-year period from the start date
        
        # Calculate the number of days completed and total days in the goal period
        total_days_in_goal = (end_date - start_date).days
        days_completed = (date.today() - start_date).days
        days_remaining = (end_date - date.today()).days

        # Ensure days_remaining is not negative
        daysLeft = max(0, days_remaining)

        # Calculate goal progress
        completed_goals = daily_goals.filter(completed=True).count()
        if total_days_in_goal > 0:
            goalProgress = (completed_goals / total_days_in_goal) * 100

        # Determine goal status based on progress
        if goalProgress >= 80:
            goalStatus = 'green'
        elif goalProgress >= 50:
            goalStatus = 'yellow'
        else:
            goalStatus = 'red'
        
        # Check if today's goal is completed
        today_goal = daily_goals.filter(date=date.today()).first()
        if today_goal and today_goal.completed:
            todayCompleted = True

        # Example performance data (for a line chart)
        performance_data = [goal.completed for goal in daily_goals.order_by('date')]
        performance_labels = [goal.date.strftime('%Y-%m-%d') for goal in daily_goals.order_by('date')]

        performance = {
            'labels': performance_labels,
            'data': performance_data
        }
    
    else:
        # No daily goals found, provide default values
        total_days_in_goal = 365
        days_completed = 0
        daysLeft = 0
        goalProgress = 0

    # Prepare data for each goal
    analytics_data = []
    for goal in daily_goals:
        goal_analytics = UserAnalyticsData.objects.filter(goal=goal)
        goal_progress = calculate_goal_progress(goal_analytics)
        
        goal_data = {
            'goal_id': goal.id,
            'goal_name': goal.title,  # Make sure to use the correct field
            'goal_progress': goalProgress,  # Update this with the calculated progress
            'days_left': daysLeft,
            'goal_status': goalStatus,
            'performance': performance,
            'today_completed': todayCompleted
        }
        analytics_data.append(goal_data)
    
    return JsonResponse({'analytics_data': analytics_data})

def calculate_goal_progress(analytics_data):
    if not analytics_data:
        return 0.0  # Return 0 if no analytics data is available
    
    total_entries = len(analytics_data)
    completed_entries = sum(data.completed for data in analytics_data)
    
    if total_entries == 0:
        return 0.0  # Return 0 if no entries are found
    
    progress_percentage = (completed_entries / total_entries) * 100
    return round(progress_percentage, 2) 


def calculate_days_left(goal):
    if not goal:
        return 0  # Return 0 if no goal is provided or found
    
    start_date = goal.date
    end_date = start_date + timedelta(days=30)  # Example: 30 days goal period
    
    days_left = (end_date - date.today()).days
    return max(0, days_left) 

def calculate_goal_status(goal_progress):
    if goal_progress >= 80:
        return 'green'  # Goal is on track or completed
    elif goal_progress >= 50:
        return 'yellow'  # Goal needs attention
    else:
        return 'red'  
