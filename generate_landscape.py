import os
import yaml
import urllib.request
import json
import time

# Custom representer to format long strings as folded block scalars (>-)
def str_presenter(dumper, data):
    if len(data) > 80 and '\n' not in data:  # Long strings without newlines
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')
    if '\n' in data:  # Strings with newlines
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)
yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

def fetch_github_description(repo_url):
    if not repo_url or not repo_url.startswith("https://github.com/"):
        return None
    
    # Extract owner and repo from "https://github.com/owner/repo"
    parts = repo_url.rstrip('/').split('/')
    if len(parts) >= 5:
        owner = parts[3]
        repo = parts[4]
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 (VKS Landscape Builder)"})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("description")
        except Exception as e:
            print(f"Warning: Failed to fetch description for {repo_url} from GitHub API. Error: {e}")
            return None
    return None

# 1. Read the target projects from vks-entries.txt
with open('vks-entries.txt', 'r') as f:
    target_projects = {line.strip() for line in f if line.strip()}

# 2. Load the main landscape template
with open('landscape-template.yml', 'r') as f:
    data = yaml.safe_load(f)

new_landscape = {'landscape': []}
logos_to_fetch = []

# 3. Filter the landscape data
for category in data.get('landscape', []):
    new_cat = {'category': None, 'name': category.get('name')}
    if 'subcategories' in category:
        new_cat['subcategories'] = []
        for subcategory in category['subcategories']:
            new_sub = {'subcategory': None, 'name': subcategory.get('name'), 'items': []}
            for item in subcategory.get('items', []):
                if item.get('name') in target_projects:
                    
                    # Ensure every item has a description
                    if 'description' not in item:
                        # Fallback 1: summary_use_case
                        if 'extra' in item and 'summary_use_case' in item['extra']:
                            item['description'] = item['extra']['summary_use_case']
                        # Fallback 2: GitHub API
                        elif 'repo_url' in item:
                            print(f"Fetching description from GitHub for {item['name']}...")
                            desc = fetch_github_description(item['repo_url'])
                            if desc:
                                item['description'] = desc
                            time.sleep(0.5) # Avoid rate limiting
                        
                    # Validate stack_overflow_url
                    if 'extra' in item and 'stack_overflow_url' in item['extra']:
                        if not item['extra']['stack_overflow_url'].startswith('https://stackoverflow.com/'):
                            del item['extra']['stack_overflow_url']

                    # Validate slack_url
                    if 'extra' in item and 'slack_url' in item['extra']:
                        if not item['extra']['slack_url'].startswith('http'):
                            item['extra']['slack_url'] = 'https://' + item['extra']['slack_url']

                    new_sub['items'].append(item)
                    if 'logo' in item:
                        logos_to_fetch.append(item['logo'])
            if new_sub['items']:
                new_cat['subcategories'].append(new_sub)
    if new_cat.get('subcategories'):
        new_landscape['landscape'].append(new_cat)

# 4. Write the filtered data to landscape.yml
with open('landscape.yml', 'w') as f:
    yaml.dump(new_landscape, f, sort_keys=False, allow_unicode=True, width=1000)

# 5. Clean up the nulls from yaml dump (category: null -> category:)
with open('landscape.yml', 'r') as f:
    content = f.read()
content = content.replace('category: null', 'category:')
content = content.replace('subcategory: null', 'subcategory:')
content = content.replace('item: null', 'item:')
with open('landscape.yml', 'w') as f:
    f.write(content)

# 6. Download the logos into hosted_logos/
os.makedirs("hosted_logos", exist_ok=True)
base_url = "https://raw.githubusercontent.com/cncf/landscape/master/hosted_logos/"

print(f"Found {len(logos_to_fetch)} logos to fetch.")
for logo in logos_to_fetch:
    path = os.path.join("hosted_logos", logo)
    if not os.path.exists(path):
        url = base_url + logo
        try:
            urllib.request.urlretrieve(url, path)
            print(f"Downloaded {logo}")
        except Exception as e:
            print(f"Failed to download {logo}: {e}")
    else:
        pass # Skip logging to reduce noise

print("Successfully updated landscape.yml and hosted_logos directory.")
