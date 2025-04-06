import requests
from bs4 import BeautifulSoup
import csv
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36"
}

def get_assessment_duration(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            duration_tag = soup.find('p', string=lambda text: text and 'Approximate Completion Time' in text)
            if duration_tag:
                return duration_tag.text.split('=')[-1].strip()
        return "Not specified"
    except Exception as e:
        print(f"Failed to fetch duration from {url}: {e}")
        return "Error"

updated_assessments = []

# Read cached file
with open('assessment_data.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        url = row['url']
        print(f"Fetching duration for: {row['name']}")
        duration = get_assessment_duration(url) if url else "Not specified"
        row['duration'] = duration
        updated_assessments.append(row)
        time.sleep(1)  # please do not block me lol

# update csv 
with open('duration.csv', mode='w', newline='', encoding='utf-8') as file:
    fieldnames = list(updated_assessments[0].keys())
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for assessment in updated_assessments:
        writer.writerow(assessment)

print(f"\nFetched durations for {len(updated_assessments)} assessments.")
