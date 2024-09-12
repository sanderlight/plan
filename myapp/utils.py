def run_simulation(yearly_goal, initial_investment, target_milestone, location):
    # Define weightings for each parameter with maximum possible scores
    weightings = {
        'initial_investment': {
            0: 10,
            100: 20,
            1000: 40,
            10000: 60,
            100000: 100,  # Maximum score for the highest investment
        },
        'target_milestone': {
            'Get a little better': 50,
            'Exceed expectation': 70,
            'Just meet the goal': 30,
            'Achieve maximum possible results': 100,  # Maximum score for the highest milestone
        },
        'location': {
            'North America': 60,
            'South America': 50,
            'Europe': 70,
            'Asia': 60,
            'Africa': 40,
            'Australia': 50,
            'Antarctica': 10,
            'Top-tier business hub': 100,  # Maximum score for the best location
        },
    }

    # Debug output for inputs
    print(f"Running simulation with:\n"
          
          f"Initial Investment: {initial_investment}\n"
          f"Target Milestone: {target_milestone}\n"
          f"Location: {location}")

    # Calculate base probability based on initial investment
    probability = weightings['initial_investment'].get(initial_investment, 0)
    print(f"Initial investment probability: {probability}%")

    # Adjust probability based on target milestone
    milestone_weighting = weightings['target_milestone'].get(target_milestone, 0)
    probability = (probability + milestone_weighting) / 2
    print(f"Target milestone weighting: {milestone_weighting}%, Probability after milestone adjustment: {probability}%")

    # Adjust probability based on location
    location_weighting = weightings['location'].get(location, 0)
    probability = (probability + location_weighting) / 2
    print(f"Location weighting: {location_weighting}%, Probability after location adjustment: {probability}%")

    # Ensure the probability is within a reasonable range
    probability = min(max(probability, 0), 100)
    print(f"Final probability (clamped between 0 and 100): {probability}%")

    # Generate a result summary
    result_summary = (
        f"Based on your inputs, the probability of achieving your goal  approximately {probability:.2f}%. "
        f"With an initial investment of ${initial_investment}, aiming to '{target_milestone}', and located in '{location}', "
        f"you have a solid foundation to work towards your goal. Consider leveraging your strengths and addressing any potential "
        f"challenges to increase your chances of success."
    )

    return probability, result_summary
