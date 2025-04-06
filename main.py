import requests
from bs4 import BeautifulSoup
import numpy as np
import csv
import time

# catalog URL
base_url = "https://www.shl.com/solutions/products/product-catalog/?start={}"

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36"
}


# Function to get assessment duration from its individual page
def get_assessment_duration(assessment_url):
    response = requests.get(assessment_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        duration_tag = soup.find('p', string=lambda text: text and 'Approximate Completion Time' in text)
        if duration_tag:
            return duration_tag.text.split('=')[-1].strip()
    return "Not specified"

all_assessments = []

# for 32 pages for now
for page in range(32):
    offset = page * 12
    url = base_url.format(offset)
    print(f"Scraping page {page + 1} with offset {offset}...")

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page at offset {offset}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr', attrs={'data-entity-id': True})

    for row in rows:
        # name and url
        test_name_tag = row.select_one('td a')
        test_name = test_name_tag.text.strip() if test_name_tag else None
        test_url = "https://www.shl.com" + test_name_tag['href'] if test_name_tag else None

        # RTS yes or no
        remote_testing_tag = row.select_one('td:nth-of-type(2) .catalogue__circle')
        remote_testing = "Yes" if remote_testing_tag and '-yes' in remote_testing_tag.get('class', []) else "No"

        # Adaptive/IRT yes or no
        adaptive_irt_tag = row.select_one('td:nth-of-type(3) .catalogue__circle')
        adaptive_irt = "Yes" if adaptive_irt_tag and '-yes' in adaptive_irt_tag.get('class', []) else "No"

        # test type
        test_type_tags = row.select('td.product-catalogue__keys span.product-catalogue__key')
        test_types = [tag.text.strip() for tag in test_type_tags]

        # duration
        # duration = get_assessment_duration(test_url) if test_url else "Not specified"

        all_assessments.append({
            'name': test_name,
            'url': test_url,
            'remote_testing': remote_testing,
            'adaptive_irt': adaptive_irt,
            # 'duration': duration,
            'test_types': test_types
        })

    time.sleep(1)

# caching
with open('assessment_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['name', 'url', 'remote_testing', 'adaptive_irt',  'test_types']) #'duration',
    writer.writeheader()
    for assessment in all_assessments:
        writer.writerow(assessment)

print(f"\n Total assessments scraped: {len(all_assessments)}")
