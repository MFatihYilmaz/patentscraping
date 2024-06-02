import os
import fitz
import re
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

def analyze_text(text):
    # Toplam kelime sayısı
    words = word_tokenize(text)
    total_words = len(words)

    # En sık geçen kelimeler ve frekansları
    word_freq = Counter(words)
    most_common_words = word_freq.most_common(5)

    # Toplam cümle sayısı
    sentences = sent_tokenize(text)
    total_sentences = len(sentences)

    # Anahtar kelimeleri tanımlamak için kelime sıklıklarını kullanabiliriz
    # Burada, en sık geçen 10 kelimeyi anahtar kelimeler olarak kabul ediyoruz
    keywords = [word for word, _ in most_common_words]

    # Bağlaçların ve ilişkilendiricilerin kullanımı
    # Örnek olarak sadece "ve" bağlacını kontrol ediyoruz
    conjunction_count = text.count(" ve ")

    # Analiz sonuçlarını döndür
    return {
        "total_words": total_words,
        "most_common_words": most_common_words,
        "total_sentences": total_sentences,
        "keywords": keywords,
        "conjunction_count": conjunction_count
    }

def get_text_from_pdf(pdf_path):
    print(pdf_path)
    try:
        pdf_doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return None

    text = ""
    for index,page in enumerate(pdf_doc):

        page_text = page.get_text("text")

        if len(page_text) == 0 and index == 0:
            print("GİRDİK:",page_text)
            return None
        text += page_text + "\n"
    text = re.sub(r"^([^\n]*)\n\s*([0-9]+)\s*\n", r"\1\n", text, flags=re.MULTILINE)
    return text

def find_claim(text):
    claim_start = text.find("STEMLER")
    claim_end = text.find("TARİFNAME")
    if claim_end>claim_start and claim_start > 0 and claim_end > 0:
        return claim_start, claim_end
    return 0,0
def find_summary(text):
    summary_start = text.find("ÖZET")
    summary_end = text.find("STEMLER")
    if summary_end > summary_start and summary_start > 0 and summary_end > 0:
        return summary_start, summary_end
    return 0,0
def pdf_analyze(pdf_paths):
    output = ""
    summary_text = []
    print("path: ",pdf_paths)
    i = 1
    for pdf_path, pdf_url in pdf_paths.items():

        text = get_text_from_pdf(pdf_path)

        if text is not None:

            summary_start, summary_end = find_summary(text)

            claim_start, claim_end = find_claim(text)

            print("ÇIKTI "+str(summary_start)+" "+str(summary_end)+" "+str(claim_start)+" "+str(claim_end))
            if summary_end>summary_start and claim_end>claim_start and summary_start != 0 and claim_start != 0:
                print(f"girdi: {pdf_url}")
                output += f"\n{str(i)}. pdf-link: {pdf_url}"
                output += (text[claim_start + 8:claim_end]).replace("\n", " ")

                summary_text.append(text[summary_start:summary_end])
                i += 1

    cleaned_text = re.sub(r'[^a-zA-ZğüşıöçĞÜŞİÖÇ0-9.,\'/=+&(){}:;?!\s]', '', output)
    return cleaned_text,summary_text
