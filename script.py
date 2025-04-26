import os
import time
import json
import base64
import requests

# Constants
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")
OWNER_ID = os.environ.get("OWNER_ID")  # <- Make sure you set this in environment variables!

if not GITHUB_TOKEN or not GITHUB_USERNAME or not OWNER_ID:
    raise EnvironmentError("Missing GITHUB_TOKEN, GITHUB_USERNAME, or OWNER_ID environment variables.")

def graphql_query(query, variables=None):
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"query": query}
    if variables:
        data["variables"] = variables

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed: {response.status_code}, {response.text}")

def rest_query(url):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"REST Query failed: {response.status_code}, {response.text}")

# Function: Calculate daily_readme (age)
def daily_readme():
    birth_year = 2004  # <-- Customize your year of birth!
    current_year = time.gmtime().tm_year
    age = current_year - birth_year
    return f"{age} years old"

# Function: Calculate total commits
def graph_commits():
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    variables = {"login": GITHUB_USERNAME}
    result = graphql_query(query, variables)
    total = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    return f"{total:,}"

# Function: Calculate total repos and stars
def graph_repos_stars():
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
          totalCount
          nodes {
            stargazerCount
          }
        }
      }
    }
    """
    variables = {"login": GITHUB_USERNAME}
    result = graphql_query(query, variables)
    repos = result["data"]["user"]["repositories"]
    repo_count = repos["totalCount"]
    stars = sum(repo["stargazerCount"] for repo in repos["nodes"])
    return f"{repo_count:,}", f"{stars:,}"

# Function: Query lines of code (loc_query)
def loc_query(owner, repo):
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 0) {
                totalCount
              }
            }
          }
        }
      }
    }
    """
    variables = {"owner": owner, "name": repo}
    result = graphql_query(query, variables)
    count = result["data"]["repository"]["defaultBranchRef"]["target"]["history"]["totalCount"]
    return count

# Function: Recursively calculate lines of code for a repository
def recursive_loc(owner, repo, data, cache_comment):
    loc = loc_query(owner, repo)
    cache_comment.append(f"loc for {repo}: {loc}")
    return owner, repo, loc

# Support functions
def force_close_file(file_obj):
    if not file_obj.closed:
        file_obj.close()

def flush_cache(file_obj):
    file_obj.flush()
    os.fsync(file_obj.fileno())

def stars_counter(repos_data):
    return sum(int(line.strip().split()[-1]) for line in repos_data)

def query_count(repos_data):
    return len(repos_data)

# Function: Cache builder
def cache_builder(data_file_path):
    with open(data_file_path, "r") as file:
        data = file.readlines()

    cache_comment = []

    for index, line in enumerate(data):
        try:
            repo_hash, owner_repo = line.strip().split(maxsplit=1)
            owner, repo_name = owner_repo.split("/")
            cache_comment.append(f"checking {repo_name}")

            loc = recursive_loc(owner, repo_name, data, cache_comment)
            data[index] = f"{repo_hash} {loc[0]}/{loc[1]} {loc[2]}\n"

            time.sleep(1)  # Avoid GitHub rate limits

        except Exception as e:
            cache_comment.append(f"Error processing line {index}: {str(e)}")
            continue

    with open(data_file_path, "w") as file:
        file.writelines(data)
        flush_cache(file)
        force_close_file(file)

    print("\n".join(cache_comment))

# Example usage
if __name__ == "__main__":
    print("Daily Readme Age:", daily_readme())
    print("Total Commits:", graph_commits())
    repo_count, stars_count = graph_repos_stars()
    print(f"Total Repositories: {repo_count}, Total Stars: {stars_count}")
