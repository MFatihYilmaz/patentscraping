from openai import OpenAI

OPENAI_API_KEY = "sk-proj-ZRvfvlDVbrNyTAvThS59T3BlbkFJ5kTOCZzvRrJwYyGVKE9r"
client = OpenAI(api_key=OPENAI_API_KEY)

def service(text):
    json = """
            {
                "No": "Burada pdf'in kaçıncı pdf olduğu yazılacak",
                "Link": "Burada pdf'in linki olacak",
                "Technologies": [
                    {
                        "TechnologyTitle": "Burada pdf'te bahsedilen teknolojinin başlığı olacak",
                        "TechnologyDescription": "Burada teknolojinin açıklaması olacak"
                    },
                    {
                        "TechnologyTitle": "Burada pdf'te bahsedilen teknolojinin başlığı olacak",
                        "TechnologyDescription": "Burada teknolojinin açıklaması olacak"
                    }
                ]
        ,
        "Techniques": [
            {
                "TechniquesTitle": "Burada kullanılan tekniğin başlığı olacak",
                "TechniquesDescription": "Burada kullanılan tekniğin açıklaması olacak"
            },
            {
                "TechniquesTitle": "Burada kullanılan tekniğin başlığı olacak",
                "TechniquesDescription": "Burada kullanılan tekniğin açıklaması olacak"
            }
        ]
    }"""

    system_prompt = f"Aşağıdaki metin kullanıcıların yanıt oluşturması için sağlanmıştır. Yanıt türü JSON olmalıdır ve lütfen kullanıcının sorusunu verilen belgeye göre yanıtlayın.:\n\n{text}\n\nKullanıcının sorusu: {json}\n\nYanıt:"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": json},
            {"role": "system", "content": system_prompt}
        ],
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content