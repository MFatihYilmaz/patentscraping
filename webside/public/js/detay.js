
document.addEventListener("DOMContentLoaded", function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);

    const patentNo = urlParams.get('patentNo');

    // Verileri kullanarak detay sayfasını doldur
    const detailContainer = document.querySelector(".col-md-8");

    // PatentNo'ya göre patenti bul
    const patent = data.find(item => item.No === patentNo);

    if (!patent) {
        console.error('Patent bulunamadı');
        return;
    }

    const { Title, Summary, Link, Technologies, Techniques, Keywords } = patent;

    const detailContent = `
        <h3>${Title}</h3>
        <p>${Summary}</p>
        <div class="technologies">
            <h4 class="white-text">Teknolojiler:</h4>
            <ul>
                ${Technologies.map(tech => `<li class="white-text">${tech.TechnologyTitle}: ${tech.TechnologyDescription}</li>`).join('')}
            </ul>
        </div>
        <div class="techniques">
            <h4 class="white-text">Teknikler:</h4>
            <ul>
                ${Techniques.map(tech => `<li class="white-text">${tech.TechniquesTitle}: ${tech.TechniquesDescription}</li>`).join('')}
            </ul>
        </div>
        <div >
            <h5 class="white-text">Keywords:</h5>
            <p>${Keywords}</p>
        </div>
        <div class="links">
            <a href="${Link}" target="_blank">Patente Git</a>
        </div>
    `;

    detailContainer.innerHTML = detailContent;
});
