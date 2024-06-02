// api.js

// Patents dizisini global olarak tanımla
let patents = [];
// Patent sınıfını tanımla
class Patent {
    constructor(No, PdfSummary, Link, Technologies, Techniques) {
        this.No = No;
        this.PdfSummary = PdfSummary;
        this.Link = Link;
        this.Technologies = Technologies;
        this.Techniques = Techniques;
    }
}

function showLoader() {
    $('#loader').addClass('visible');
}

function hideLoader() {
    $('#loader').removeClass('visible');
}

function createCard(patent) {
    const card = document.createElement("div");
    card.classList.add("card");

    const cardContent = `
        <h3>No: ${patent.No}</h3>
        <p>${patent.PdfSummary}</p>
        <div class="technologies">
            <h4 class="white-text">Technologies:</h4>
            <ul>
                ${patent.Technologies.map(tech => `<li class="white-text">${tech.TechnologyTitle}: ${tech.TechnologyDescription}</li>`).join('')}
            </ul>
        </div>
        <div class="techniques">
            <h4 class="white-text">Techniques:</h4>
            <ul>
                ${patent.Techniques.map(tech => `<li class="white-text">${tech.TechniquesTitle}: ${tech.TechniquesDescription}</li>`).join('')}
            </ul>
        </div>
        <div class="links">
            <a href="${patent.Link}" target="_blank">Patente Git</a>
            <a href="/detay?patentNo=${patent.No}">Detay</a>
        </div>
    `;

    card.innerHTML = cardContent;
    return card;
}

showLoader(); // Loader'ı göster

fetch("http://127.0.0.1:5000/api/patent?q=kahve&words=makine&startDate=03-03-2014&endDate=03-03-2024")
    .then(response => {
        // HTTP yanıtı kontrolü
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // JSON verisini işleme
        console.log(data);

        patents = data.map(patentData => {
            // Her bir JSON verisi için Patent nesnesi oluştur
            const technologies = patentData.Technologies.map(tech => ({ TechnologyTitle: tech.TechnologyTitle, TechnologyDescription: tech.TechnologyDescription }));
            const techniques = patentData.Techniques.map(tech => ({ TechniquesTitle: tech.TechniquesTitle, TechniquesDescription: tech.TechniquesDescription }));
            return new Patent(patentData.No, patentData.PdfSummary, patentData.Link, technologies, techniques);
        });

        const patentCardsContainer = document.getElementById("patent-cards");

        patents.forEach(patent => {
            const card = createCard(patent);
            patentCardsContainer.appendChild(card);
        });

        hideLoader(); // Loader gizle
    })
    .catch(error => {
        // Hata durumunda işlemler
        console.error('Hata:', error);
        hideLoader(); // Loader gizle
    });

// Detay sayfasına tıklanan kartın verilerini aktar
$(document).on("click", ".detail-link", function () {
    // Tıklanan kartın verilerini al
    const card = $(this).closest(".card");
    const No = card.find(".card-no").text();
    const PdfSummary = card.find(".card-summary").text();
    const Link = card.find(".card-link").attr("href");
    const Technologies = [];
    card.find(".card-technology").each(function () {
        Technologies.push({
            TechnologyTitle: $(this).find(".technology-title").text(),
            TechnologyDescription: $(this).find(".technology-description").text()
        });
    });
    const Techniques = [];
    card.find(".card-technique").each(function () {
        Techniques.push({
            TechniquesTitle: $(this).find(".technique-title").text(),
            TechniquesDescription: $(this).find(".technique-description").text()
        });
    });

    // Detay sayfasına verileri aktar
    window.location.href = `/detay?patentNo=${No}&PdfSummary=${PdfSummary}&Link=${Link}&Technologies=${JSON.stringify(Technologies)}&Techniques=${JSON.stringify(Techniques)}`;
});

