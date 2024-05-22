import asyncio
import json

import aiohttp
from pyppeteer import launch
from pdf import pdf_analyze
import re
from service import service
import time
import concurrent.futures
from urllib.parse import quote

from dataclasses import dataclass, field
from typing import List

baslangic_zamani = time.time()

patents = []
pdf_paths = {}

class Patent:
    def __init__(self, title, pdf_link, publish_date):
        self.title = title
        self.pdf_link = pdf_link
        self.publish_date = publish_date

async def download_pdf(session, url, filename):
    async with session.get(url) as response:
        if response.status == 200:
            content = await response.read()
            await asyncio.to_thread(write_pdf, filename, content)
            pdf_paths[filename] = url

def write_pdf(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)


async def visit_and_fetch(url):
    async with aiohttp.ClientSession() as session:
        browser = await launch(handleSIGINT=False,
                               handleSIGTERM=False,
                               handleSIGHUP=False,
                               headless=True
                               )
        print(url)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'domcontentloaded'})
        await page.waitForSelector('td.MuiTableCell-root')
        numofpatent = await page.querySelector('div#search-results p')
        numofpatent = await (await numofpatent.getProperty('textContent')).jsonValue()
        num = int(str(numofpatent).split(' ')[0])

        if numofpatent is None:
            print('girdi')
            return "String is empty"
        num = 10 if num > 10 else num
        tasks = []

        for i in range(num):
            pdfId = await (
                await (await page.querySelector(f'#applicationNumber-{i}')).getProperty('textContent')).jsonValue()
            title = await (
                await (await page.querySelector(f'th#enhanced-table-{i}')).getProperty('textContent')).jsonValue()
            date = await (
                await (await page.querySelector(f'td#applicationDate-{i}')).getProperty('textContent')).jsonValue()
            patent = Patent(title, pdfId, date)
            patents.append(patent)
            download_url = f'https://portal.turkpatent.gov.tr/anonim/arastirma/patent/sonuc/dosya?patentAppNo={pdfId}&documentsTpye=all'
            task = asyncio.create_task(download_pdf(session, download_url, f"pdf{i}.pdf"))
            print(i)
            tasks.append(task)
        print(patents)
        await asyncio.gather(*tasks)

async def main(url):
    tasks = [visit_and_fetch(url)]
    results = await asyncio.gather(*tasks)
    if 'String is empty' in results:
        return False

def mainfunc(q):
    url = f'https://www.turkpatent.gov.tr/arastirma-yap?form=patent&params=%257B%2522title%2522%253A%2522{quote(q)}%2522%257D&run=true'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url))
    output,summ = pdf_analyze(pdf_paths)
    output = output.split("\n")
    output.pop(0)

    num_threads = len(output)
    json_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # İstekleri gönder
        future_to_prompt = {executor.submit(service, prompt): prompt for prompt in output}
        # Sonuçları al
        for future in concurrent.futures.as_completed(future_to_prompt):
            prompt = future_to_prompt[future]
            try:
                response = future.result()
                json_text = json.loads(response)
                sum_index=output.index(prompt)
                json_text["Summary"]=summ[sum_index]
                print(json_text)

                json_list.append(json_text)
                print(f"Response for '{prompt}': {response}")
            except Exception as exc:
                print(f"An error occurred for '{prompt}': {exc}")
        json_data = json.dumps(json_list,ensure_ascii=False,indent=4)


        with open("combined.json","w+",encoding="utf-8") as f:
            f.write(json_data)

    #service(output)
    bitis_zamani = time.time()
    gecen_sure = bitis_zamani - baslangic_zamani
    print(gecen_sure)

    return json_data

if __name__=="__main__":
    mainfunc('kahve')