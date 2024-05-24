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
    try:
        pdf_doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return None

    text = ""
    for page in pdf_doc:
        page_text = page.get_text("text")
        text += page_text + "\n"
    text = re.sub(r"^([^\n]*)\n\s*([0-9]+)\s*\n", r"\1\n", text, flags=re.MULTILINE)
    return text


def find_claim(text):
    claim_start = text.find("İSTEMLER")
    claim_end = text.find("TARİFNAME")
    return claim_start, claim_end


def find_summary(text):
    summary_start = text.find("ÖZET")
    summary_end = text.find("İSTEMLER")
    return summary_start, summary_end


pdf_paths = ["pdf0.pdf", "pdf2.pdf", "pdf3.pdf", "pdf4.pdf", "pdf5.pdf", "pdf6.pdf", "pdf7.pdf", "pdf8.pdf", "pdf9.pdf"]


def pdf_analyze(pdf_paths):
    output = ""
    summary_text = []
    i = 1
    for pdf_path, pdf_url in pdf_paths.items():
        output_filename = os.path.splitext(pdf_path)[0] + ".txt"

        text = get_text_from_pdf(pdf_path)
        if text is None:
            continue

        summary_start, summary_end = find_summary(text)
        if summary_start is None:
            continue

        claim_start, claim_end = find_claim(text)

        # print(f"**Özet:**")
        # print(text[summary_start+4:summary_end])

        # print(f"**İstemler:**")
        # output += "\n"+pdf_path+" link: "+pdf_url

        output += f"\n{str(i)}. pdf-link: {pdf_url}"
        output += (text[claim_start + 8:claim_end]).replace("\n", " ")

        cleaned_text = re.sub(r'[^a-zA-ZğüşıöçĞÜŞİÖÇ0-9.,\'/=+&(){}:;?!\s]', '', output)
        # print(pdf_path+" link: "+pdf_url)
        # print(text[claim_start+8:claim_end])
        # Özet ve istemleri kullanarak metin analizini yap
        summary_text.append(text[summary_start:summary_end])
        claim_text = text[claim_start:claim_end]

        # claim_text içindeki tüm noktalama işaretlerini silme
        claim_text = re.sub(r'[^\w\s]', '', claim_text)

        claim_analysis = analyze_text(claim_text)
        i += 1
    '''    # Analiz sonuçlarını görüntüle
        print("**Özet Analizi:**")
        print("Toplam Kelime Sayısı:", summary_analysis["total_words"])
        print("En Sık Geçen Kelimeler:", summary_analysis["most_common_words"])
        print("Toplam Cümle Sayısı:", summary_analysis["total_sentences"])
        print("Anahtar Kelimeler:", summary_analysis["keywords"])
        print("Bağlaç (ve) Sayısı:", summary_analysis["conjunction_count"])
        print("\n")

        print("**İstemler Analizi:**")
        print("Toplam Kelime Sayısı:", claim_analysis["total_words"])
        print("En Sık Geçen Kelimeler:", claim_analysis["most_common_words"])
        print("Toplam Cümle Sayısı:", claim_analysis["total_sentences"])
        print("Anahtar Kelimeler:", claim_analysis["keywords"])
        print("Bağlaç (ve) Sayısı:", claim_analysis["conjunction_count"])
    '''

    return cleaned_text,summary_text