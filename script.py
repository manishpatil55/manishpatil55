import os
import requests
import datetime
from pathlib import Path

# GitHub API to get your stats
GITHUB_API_URL = "https://api.github.com/users/{}/repos"
GITHUB_USERNAME = os.getenv("USER_NAME")  # Set this in the secrets
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # GitHub token for accessing stats

# Path to your SVG template
SVG_FILE_PATH = dark_mode.svg

# Your birthdate
BIRTHDATE = datetime.datetime(2004, 11, 8)

# Function to get GitHub stats
def get_github_stats():
    response = requests.get(GITHUB_API_URL.format(GITHUB_USERNAME), headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    })
    if response.status_code == 200:
        repos = response.json()
        total_repos = len(repos)
        total_commits = sum([repo['stargazers_count'] for repo in repos])
        total_stars = sum([repo['watchers_count'] for repo in repos])
        lines_of_code = 371888  # Just a placeholder, you can fetch it dynamically if needed
        return total_repos, total_commits, total_stars, lines_of_code
    else:
        return 0, 0, 0, 0

def get_system_stats():
    # Get current time and uptime
    uptime_seconds = float(os.popen("cat /proc/uptime").read().split()[0])  # Convert to float
    uptime = datetime.timedelta(seconds=uptime_seconds)  # Use the float value here
    system_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_date = datetime.datetime.now().strftime('%d/%m/%Y')  # Format date as DD/MM/YYYY
    return uptime, system_time, current_date


# Function to calculate age (uptime)
def calculate_age(birthdate):
    today = datetime.datetime.today()
    age_years = today.year - birthdate.year
    age_months = today.month - birthdate.month
    age_days = today.day - birthdate.day

    if age_months < 0:
        age_years -= 1
        age_months += 12

    if age_days < 0:
        age_months -= 1
        if age_months < 0:
            age_years -= 1
            age_months += 12
        # Adjust for the days of the previous month
        previous_month = today.replace(year=today.year, month=today.month - 1 if today.month > 1 else 12)
        age_days += (today - previous_month.replace(day=1)).days

    return age_years, age_months, age_days

# Function to update SVG
def update_svg(total_repos, total_commits, total_stars, lines_of_code, uptime, system_time, current_date, age_years, age_months, age_days):
    # Open the template SVG file
    with open(SVG_FILE_PATH, "r") as file:
        svg_content = file.read()

    # Replace placeholders with dynamic data
    svg_content = svg_content.replace("<tspan x=\"370\" y=\"70\" class=\"keyColor\">OS</tspan>: <tspan class=\"valueColor\">Windows 10+, iOS</tspan>",
                                      f"<tspan x=\"370\" y=\"70\" class=\"keyColor\">OS</tspan>: <tspan class=\"valueColor\">Linux</tspan>")

    svg_content = svg_content.replace("<tspan x=\"370\" y=\"90\" class=\"keyColor\">Uptime</tspan>: <tspan class=\"valueColor\">19 years, 9 months, 6 days</tspan>",
                                      f"<tspan x=\"370\" y=\"90\" class=\"keyColor\">Uptime</tspan>: <tspan class=\"valueColor\">{age_years} years, {age_months} months, {age_days} days</tspan>")

    svg_content = svg_content.replace("<tspan x=\"370\" y=\"110\" class=\"keyColor\">Host</tspan>: <tspan class=\"valueColor\">G H Raisoni College of Engineering</tspan><tspan class=\"commentColor\"> #RIT</tspan>",
                                      f"<tspan x=\"370\" y=\"110\" class=\"keyColor\">Host</tspan>: <tspan class=\"valueColor\">{system_time}</tspan><tspan class=\"commentColor\"> #Updated</tspan>")

    svg_content = svg_content.replace("<tspan x=\"370\" y=\"490\" class=\"keyColor\">Repos</tspan>: <tspan class=\"valueColor\">43</tspan> {<tspan class=\"keyColor\">Contrib_to</tspan>: <tspan class=\"valueColor\">37</tspan>}",
                                      f"<tspan x=\"370\" y=\"490\" class=\"keyColor\">Repos</tspan>: <tspan class=\"valueColor\">{total_repos}</tspan> <tspan class=\"keyColor\">Contrib_to</tspan>: <tspan class=\"valueColor\">{total_commits}</tspan>")
    # Add the age in the appropriate place in your SVG template
    svg_content = svg_content.replace("<tspan x=\"370\" y=\"150\" class=\"keyColor\">Age</tspan>: <tspan class=\"valueColor\">18 years, 6 months, 12 days</tspan>",
                                      f"<tspan x=\"370\" y=\"150\" class=\"keyColor\">Age</tspan>: <tspan class=\"valueColor\">{age_years} years, {age_months} months, {age_days} days</tspan>")

    
    # Save updated SVG to file
    with open(SVG_FILE_PATH, "w") as file:
        file.write(svg_content)

if __name__ == "__main__":
    # Get stats
    total_repos, total_commits, total_stars, lines_of_code = get_github_stats()
    uptime, system_time, current_date = get_system_stats()
    age_years, age_months, age_days = calculate_age(BIRTHDATE)

    # Update the SVG file
    update_svg(total_repos, total_commits, total_stars, lines_of_code, uptime, system_time, current_date, age_years, age_months, age_days)
