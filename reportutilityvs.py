import json
import os
from datetime import datetime

# Function to read JSON and count events with date conversion
def count_events(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    counts = {'acceptance': 0, 'suggestion': 0}
    lines = {'acceptance': 0, 'suggestion': 0}
    events_by_date = {'acceptance': {}, 'suggestion': {}}
    
    for entry in data:
        event_type = entry['event']
        timestamp = entry['timestamp'] / 1000  # Convert to seconds
        date_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
        code_lines = entry['code'].count('\n') + 1  # Count lines in the code
        
        if event_type in counts:
            counts[event_type] += 1
            lines[event_type] += code_lines
            if date_str not in events_by_date[event_type]:
                events_by_date[event_type][date_str] = 0
            events_by_date[event_type][date_str] += 1
    
    return counts, lines, events_by_date

# Function to generate HTML with CSS-styled horizontal bars and a line chart
def generate_html(html_file_path, counts, lines, events_by_date):
    # Calculate total events
    total_events = counts['acceptance'] + counts['suggestion']
    
    # Define maximum width for the bars in pixels
    max_width = 400  
    
    # Prepare data for the line chart
    dates = sorted(events_by_date['acceptance'].keys())
    productivity_data = []
    labels = []
    
    for date in dates:
        total_by_date = events_by_date['acceptance'].get(date, 0) + events_by_date['suggestion'].get(date, 0)
        if total_by_date > 0:
            productivity_by_date = (events_by_date['acceptance'].get(date, 0) / total_by_date) * 100
        else:
            productivity_by_date = 0
        labels.append(date)
        productivity_data.append(productivity_by_date)
    
    # Generate HTML content with CSS-styled bars and Chart.js line chart
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Event Statistics</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                display: flex;
                justify-content: space-between;
            }}
            .chart-container {{
                width: 60%;
                text-align: left;
            }}
            .productivity-container {{
                width: 35%;
                text-align: left;
                padding-right: 20px;
                border-right: 2px solid #ccc; /* Add a border for separation */
            }}
            .bar {{
                height: 30px;
                margin-bottom: 10px;
                color: white;
                text-align: right;
                line-height: 30px;
                padding-right: 10px;
                border-radius: 5px;
            }}
            .acceptance-bar {{
                background-color: #4CAF50;
                width: {counts['acceptance'] / total_events * max_width}px;
            }}
            .suggestion-bar {{
                background-color: #FF5722;
                width: {counts['suggestion'] / total_events * max_width}px;
            }}
            .productivity-bar {{
                background-color: #2196F3;
                margin-top: 10px;
            }}
            .events {{
                margin-top: 20px;
                text-align: left;
                display: inline-block;
            }}
            .event-category {{
                margin-bottom: 20px;
            }}
            .chart-container {{
                margin-top: 20px;
            }}
            .productivity-header {{
                color: grey;
            }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="productivity-container">
            <h1>Event Statistics</h1>
            <h1 class="productivity-header">Productivity Information</h1>
            <div class="bar acceptance-bar">Acceptance: {counts['acceptance']}</div>
            <div class="bar suggestion-bar">Suggestion: {counts['suggestion']}</div>
            <div class="bar productivity-bar" style="width: {counts['acceptance'] / total_events * max_width}px;">
                Productivity: {((counts['acceptance'] / total_events) * 100):.2f}%
            </div>
            <p>Total Lines (Acceptance): {lines['acceptance']}</p>
            <p>Total Lines (Suggestion): {lines['suggestion']}</p>
            <p>Total Lines: {lines['acceptance'] + lines['suggestion']}</p>
        </div>
        <div class="chart-container">
            <h2>Events by Date</h2>
    """

    # Generate bars for productivity percentage by date and lines of code
    for date in events_by_date['acceptance'].keys():
        total_by_date = events_by_date['acceptance'].get(date, 0) + events_by_date['suggestion'].get(date, 0)
        if total_by_date > 0:
            productivity_by_date = (events_by_date['acceptance'].get(date, 0) / total_by_date) * 100
            productivity_width = (productivity_by_date / 100) * max_width
            lines_by_date = events_by_date['acceptance'].get(date, 0) + events_by_date['suggestion'].get(date, 0)
            html_content += f"""
            <div class="event-category">
                <h3>{date}</h3>
                <div class="bar productivity-bar" style="width: {productivity_width}px;">
                    Productivity: {productivity_by_date:.2f}%
                </div>
                <p>Total Lines: {lines_by_date}</p>
            </div>
            """

    # Close HTML content and add the line chart
    html_content += f"""
            <h2>Productivity Trend Over Time</h2>
            <canvas id="productivityChart" width="400" height="200"></canvas>
            <script>
                const ctx = document.getElementById('productivityChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(labels)},
                        datasets: [{{
                            label: 'Productivity (%)',
                            data: {json.dumps(productivity_data)},
                            borderColor: '#2196F3',
                            backgroundColor: 'rgba(33, 150, 243, 0.2)',
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        scales: {{
                            x: {{
                                beginAtZero: true
                            }},
                            y: {{
                                beginAtZero: true,
                                ticks: {{
                                    callback: function(value) {{
                                        return value + '%';
                                    }}
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: true
                            }}
                        }}
                    }}
                }});
            </script>
        </div>
    </body>
    </html>
    """

    with open(html_file_path, 'w') as file:
        file.write(html_content)

# Main function to process JSON and generate HTML
def main():
    # Ask user for JSON file path and HTML output path
    json_file_path = input("Enter the path to the JSON file: ")
    html_file_path = input("Enter the path to save the generated HTML report: ")
    
    # Ensure paths are valid
    if not os.path.isfile(json_file_path):
        print("Invalid JSON file path. Please check the path and try again.")
        return
    
    html_directory = os.path.dirname(html_file_path)
    if not os.path.exists(html_directory):
        os.makedirs(html_directory)
    
    # Process the JSON and generate the HTML report
    counts, lines, events_by_date = count_events(json_file_path)
    generate_html(html_file_path, counts, lines, events_by_date)
    print(f'HTML file generated at: {html_file_path}')

# Run the main function
if __name__ == '__main__':
    main()
