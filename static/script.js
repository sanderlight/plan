function fetchAnalyticsData() {
    $.ajax({
        url: '/api/analytics/',
        type: 'GET',
        success: function (data) {
            console.log('Received data:', data); // Log the data received
            if (data && Array.isArray(data.analytics_data)) {
                updateAnalyticsUI(data.analytics_data);
            } else {
                console.error('Invalid response format:', data);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error('AJAX request failed:', textStatus, errorThrown);
        }
    });
}

function updateAnalyticsUI(analyticsData) {
    // Update the goal progress card
    if (analyticsData.length > 0) {
        let overallProgress = 0;
        let totalGoals = analyticsData.length;

        analyticsData.forEach(function(goal) {
            if (goal.goal_progress != null) {
                overallProgress += goal.goal_progress;
            }
        });

        const averageProgress = totalGoals ? (overallProgress / totalGoals) : 0;
        $('.circular-chart .circle').attr('stroke-dasharray', `${averageProgress}, 100`);
        $('.circular-chart .percentage').text(`${Math.round(averageProgress)}%`);
    }

    // Update the goal status card
    if (analyticsData.length > 0) {
        const status = analyticsData[0].goal_status || 'default'; // Default status if missing
        $('.status-circle').removeClass('green yellow red').addClass(status);
    }

    // Update the days left card
    if (analyticsData.length > 0) {
        const daysLeft = analyticsData[0].days_left || 0; // Default value if missing
        $('.days-left').text(`${daysLeft} Days`);
    }

    // Update the performance chart
    if (analyticsData.length > 0) {
        const ctx = document.getElementById('performanceChart').getContext('2d');
        const data = {
            labels: [],
            datasets: [{
                label: 'Performance',
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        };

        analyticsData.forEach(function(goal) {
            if (goal.goal_name && goal.goal_progress != null) {
                data.labels.push(goal.goal_name);
                data.datasets[0].data.push(goal.goal_progress);
            }
        });

        // Destroy the existing chart if it exists to prevent multiple charts stacking up
        if (window.performanceChart) {
            window.performanceChart.destroy();
        }

        window.performanceChart = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}


querySelector('.logo-box').addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('close');
});





document.getElementById('goal-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    const form = event.target;
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Example of updating the UI with a success message
            const successMessage = document.createElement('p');
            successMessage.textContent = 'Goal status updated successfully!';
            successMessage.style.color = 'green';
            form.appendChild(successMessage);
            
            // Optionally, you could clear any existing message after a few seconds
            setTimeout(() => {
                successMessage.remove();
            }, 3000);
        } else {
            alert('Failed to update goal status.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the goal status.');
    });
});

$(document).ready(function () {
    var associatedDates = [];
    var selectedDate = moment().format('YYYY-MM-DD'); // Default to today

    // Initialize FullCalendar
    var calendar = $('#calendar').fullCalendar({
        selectable: true,
        selectHelper: true,
        events: [],
        selectAllow: function(selectInfo) {
            var date = selectInfo.start.format('YYYY-MM-DD');
            return associatedDates.includes(date);  // Allow selection only if the date is associated with the selected yearly goal
        },
        select: function(start) {
            selectedDate = start.format('YYYY-MM-DD');
            fetchDailyGoals(selectedDate);
        }
    });

    // Handle Yearly Goal Selection
    $('#yearlyGoalSelect').on('change', function() {
        var selectedYearlyGoalId = $(this).val();

        // Update the calendar with highlighted days for the selected yearly goal
        updateCalendarWithGoals(selectedYearlyGoalId);

        // Fetch and display the daily goals for the selected date (if any)
        fetchDailyGoals(selectedDate);
    });

    function fetchDailyGoals(date) {
        var selectedYearlyGoalId = $('#yearlyGoalSelect').val();
        if (!selectedYearlyGoalId) {
            return;
        }
    
        $.ajax({
            url: '/day/',
            type: 'GET',
            data: {
                'date': date,
                'yearly_goal_id': selectedYearlyGoalId
            },
            success: function (data) {
                if (data.daily_goals && data.daily_goals.length > 0) {
                    $('#dailyGoalsCard').html('');
                    var goalContent = '';
                    var csrfToken = '{{ csrf_token }}'; // Ensure the CSRF token is passed into the template
    
                    data.daily_goals.forEach(function (goal) {
                        goalContent += `
                            <div class="goal-detail">
                                <h1>Daily Goal Details</h1>
                                <p>Title: ${goal.title}</p>
                                <p>Description: ${goal.description}</p>
                                <p>Date: ${goal.date}</p>
                                <p>Status: ${goal.completed ? 'Completed' : 'Not Completed'}</p>
                                <form class="update-goal-status" data-goal-id="${goal.id}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                    <input type="radio" name="completed" value="true" ${goal.completed ? 'checked' : ''}> Completed
                                    <input type="radio" name="completed" value="false" ${!goal.completed ? 'checked' : ''}> Not Completed
                                    <button type="submit">Update Status</button>
                                </form>
                            </div>
                        `;
                    });
    
                    $('#dailyGoalsCard').html(goalContent).show();
    
                    // Attach event listeners to the forms for status update
                    $('.update-goal-status').on('submit', function(event) {
                        event.preventDefault();
                        var form = $(this);
                        var goalId = form.data('goal-id');
                        var status = form.find('input[name="completed"]:checked').val();
    
                        updateGoalStatus(goalId, status);
                    });
    
                } else {
                    $('#dailyGoalsCard').html('<p>No daily goal found for the selected date.</p>').show();
                }
            },
            error: function () {
                $('#dailyGoalsCard').html('<p>Failed to fetch daily goal.</p>').show();
            }
        });
    }
    
    function updateGoalStatus(goalId, status) {
        var csrfToken = getCookie('csrftoken'); // Function to get CSRF token from cookies
    
        $.ajax({
            url: `/update-daily-goal-status/${goalId}/`,
            type: 'POST',
            data: {
                'completed': status,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function (data) {
                alert('Goal status updated successfully!');
                fetchDailyGoals(selectedDate);  // Refresh the goals after update
            },
            error: function () {
                alert('An error occurred while updating the goal status.');
            }
        });
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    

    function updateCalendarWithGoals(yearlyGoalId) {
        $.ajax({
            url: '/get-yearly-goal-dates/',
            type: 'GET',
            data: {
                'yearly_goal_id': yearlyGoalId
            },
            success: function (data) {
                associatedDates = [];  // Clear the previous associated dates
                var events = [];
                if (data.goal_dates && data.goal_dates.length > 0) {
                    data.goal_dates.forEach(function (date) {
                        associatedDates.push(date);
                        events.push({
                            title: 'Goal',
                            start: date,
                            allDay: true,
                            backgroundColor: '#28a745',
                            borderColor: '#28a745'
                        });
                    });
                }
                // Remove all events and add the new ones
                $('#calendar').fullCalendar('removeEvents');
                $('#calendar').fullCalendar('addEventSource', events);
            },
            error: function () {
                console.log('Failed to fetch goal dates.');
            }
        });
    }
});


