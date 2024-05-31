import asyncio
import json
import math
import aiohttp
import os
from playwright.async_api import async_playwright
from pdf import pdf_analyze
from dataclasses import dataclass, field
import concurrent.futures
import re
from service import service
from typing import List
import time
import glob
from urllib.parse import quote

baslangic_zamani = time.time()

patents = {}
pdf_paths = {}

class Patent:
    def __init__(self, index,title, pdf_link, publish_date):
        self.index=index
        self.title = title
        self.pdf_link = pdf_link
        self.publish_date = publish_date

    def to_dict(self):
        return {
            'index':self.index,
            'title': self.title,
            'pdf_link': self.pdf_link,
            'publish_date': self.publish_date
        }

async def download_pdf(session, url, filename):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                await asyncio.to_thread(write_pdf, filename, content)
                pdf_paths[filename] = url
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {filename}, status code: {response.status}")

    except Exception as e:
        print(f"Exception during download:{filename,e}")
        return e

def write_pdf(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)

async def visit_and_fetch(url):
    async with aiohttp.ClientSession() as session:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            print(url)
            page = await browser.new_page()
            await page.goto(url, wait_until='domcontentloaded')
            await page.wait_for_timeout(10000)
            not_found = await page.query_selector('div#search-results div h6')
            if not_found is not None:
                raise Exception("Pdf not found")
            numofpatent_element = await page.query_selector('div#search-results p')
            numofpatent = await numofpatent_element.text_content()
            await page.click('#__next div section div span.jss92')

            await page.evaluate('''() => {
                const element = document.querySelector('input.MuiSwitch-input');
                element.click();
                return element !== null && element.checked;
            }''')
            await page.wait_for_selector('input.MuiSwitch-input')
            num = int(str(numofpatent).split(' ')[0].replace(".",""))


            num = min(100, num)
            tasks = []
            pdfs_per_page = 20
            click_length = max(math.ceil(num / pdfs_per_page) - 1,1)
            previous_height = await page.evaluate('document.body.scrollHeight')
            for page_number in range(click_length):
                print("girdi", page_number)
                for i in range(min(pdfs_per_page,num)):
                    print("--------", (pdfs_per_page * page_number))
                    pdf_id_element = await page.query_selector(f'#applicationNumber-{(pdfs_per_page * page_number) + i}')
                    print("id element: ",pdf_id_element)
                    pdf_id = await pdf_id_element.text_content()

                    title_element = await page.query_selector(f'th#enhanced-table-{(pdfs_per_page * page_number) + i}')
                    title = await title_element.text_content()
                    date_element = await page.query_selector(f'td#applicationDate-{(pdfs_per_page * page_number) + i}')
                    date = await date_element.text_content()
                    
                    download_url = f'https://portal.turkpatent.gov.tr/anonim/arastirma/patent/sonuc/dosya?patentAppNo={pdf_id}&documentsTpye=all'
                    patent = Patent(((pdfs_per_page * page_number) + i),title, download_url, date)
                    patents[download_url]=patent
                    task = asyncio.create_task(download_pdf(session, download_url, f"pdf{(pdfs_per_page * page_number) + i}.pdf"))
                    tasks.append(task)
                print("FOR BİTTİ")
                if num > 20:
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight - 1200)')
                    await page.wait_for_selector(f'td#applicationNumber-{(pdfs_per_page * (page_number + 1))}')
                    new_height = await page.evaluate('document.body.scrollHeight')
                    if new_height == previous_height:
                        print('HATAAAAAAAAAAAAAAAAAAAAAA')
                        break
                    previous_height = new_height

            await asyncio.gather(*tasks)
            await browser.close()

async def main(url):
    await visit_and_fetch(url)

def delete_files(pattern):
    files = glob.glob(pattern)
    for file in files:
        try:
            os.remove(file)
            print(f"{file} silindi.")
        except OSError as e:
            print(f"{file} silinirken hata oluştu: {e}")

def mainfunc(sum='', title='', start_date='', end_date=''):
    delete_files("*.pdf")
    url = f'https://www.turkpatent.gov.tr/arastirma-yap?form=patent&params=%257b%2522abstracttr%2522%253a%2522{quote(sum)}%2522%252c%2522title%2522%253a%2522{quote(title)}%2522%252c%2522bulletinDate%2522%253a%2522{quote(start_date)}%2522%252c%2522bulletinDateLast%2522%253a%2522{quote(end_date)}%2522%257d&run=true'
    asyncio.run(main(url))
    time.sleep(1)
    output, summ = pdf_analyze(pdf_paths)
    output = output.split("\n")
    output.pop(0)

    num_threads = len(output)


    print("num threads: ", num_threads)
    json_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_prompt = {executor.submit(service, prompt): prompt for prompt in output}
        for future in concurrent.futures.as_completed(future_to_prompt):
            prompt = future_to_prompt[future]
            try:
                response = future.result()
                json_text = json.loads(response)
                sum_index = output.index(prompt)
                json_text["Summary"] = summ[sum_index]
                patent_index = json_text.get('Link')
                patentval = patents.get(patent_index)
                json_text['patent_data'] = patentval.to_dict()
                print(patentval.to_dict()["title"])
                json_list.append(json_text)
                print(f"Response for '{prompt}': {response}")
            except Exception as exc:
                print(f"An error occurred for '{prompt.splitlines()[0]}': {exc}")
        json_data = json.dumps(json_list, ensure_ascii=False, indent=4)
        print(json_data)
        with open("combined.json", "w+", encoding="utf-8") as f:
            f.write(json_data)

    bitis_zamani = time.time()
    gecen_sure = bitis_zamani - baslangic_zamani
    print(gecen_sure)

    return json_data


if __name__ == "__main__":
    mainfunc(title='rejenerasyon')
