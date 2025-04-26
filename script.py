import os
import requests
import datetime
from pathlib import Path

# GitHub API to get your stats
GITHUB_API_URL = "https://api.github.com/users/{}/repos"
GITHUB_USERNAME = os.getenv("USER_NAME")  # Set this in the secrets
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # GitHub token for accessing stats

# Path to your SVG template
SVG_FILE_PATH = "dark_mode.svg"

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

# Function to get current system stats
def get_system_stats():
    # Get current time and uptime
    uptime = datetime.timedelta(seconds=int(os.popen("cat /proc/uptime").read().split()[0]))
    system_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return uptime, system_time

# Function to update SVG
def update_svg(total_repos, total_commits, total_stars, lines_of_code, uptime, system_time):
    # Open the template SVG file
    with open(SVG_FILE_PATH, "r") as file:
        svg_content = file.read()

    # Replace placeholders with dynamic data
    svg_content = svg_content.replace("<tspan x=\"370\" y=\"70\" class=\"keyColor\">OS</tspan>: <tspan class=\"valueColor\">Windows 10+, iOS</tspan>",
                                      f"<tspan x=\"370\" y=\"70\" class=\"keyColor\">OS</tspan>: <tspan class=\"valueColor\">Linux</tspan>")

    svg_content = svg_content.replace("<tspan x=\"370\" y=\"90\" class=\"keyColor\">Uptime</tspan>: <tspan class=\"valueColor\">19 years, 9 months, 6 days</tspan>",
                                      f"<tspan x=\"370\" y=\"90\" class=\"keyColor\">Uptime</tspan>: <tspan class=\"valueColor\">{uptime}</tspan>")

    svg_content = svg_content.replace("<tspan x=\"370\" y=\"110\" class=\"keyColor\">Host</tspan>: <tspan class=\"valueColor\">G H Raisoni College of Engineering</tspan><tspan class=\"commentColor\"> #RIT</tspan>",
                                      f"<tspan x=\"370\" y=\"110\" class=\"keyColor\">Host</tspan>: <tspan class=\"valueColor\">{system_time}</tspan><tspan class=\"commentColor\"> #Updated</tspan>")

    svg_content = svg_content.replace("<tspan x=\"370\" y=\"490\" class=\"keyColor\">Repos</tspan>: <tspan class=\"valueColor\">43</tspan> {<tspan class=\"keyColor\">Contrib_to</tspan>: <tspan class=\"valueColor\">64</tspan>} | <tspan class=\"keyColor\">Commmits</tspan>: <tspan class=\"valueColor\">1,155  </tspan> | <tspan class=\"keyColor\">Stars</tspan>: <tspan class=\"valueColor\">37</tspan>",
                                      f"<tspan x=\"370\" y=\"490\" class=\"keyColor\">Repos</tspan>: <tspan class=\"valueColor\">{total_repos}</tspan> {<tspan class=\"keyColor\">Contrib_to</tspan>: <tspan class=\"valueColor\">{total_commits}</tspan>} | <tspan class=\"keyColor\">Stars</tspan>: <tspan class=\"valueColor\">{total_stars}</tspan}")

    # Save updated SVG to file
    with open(SVG_FILE_PATH, "w") as file:
        file.write(svg_content)

if __name__ == "__main__":
    # Get stats
    total_repos, total_commits, total_stars, lines_of_code = get_github_stats()
    uptime, system_time = get_system_stats()

    # Update the SVG file
    update_svg(total_repos, total_commits, total_stars, lines_of_code, uptime, system_time)
