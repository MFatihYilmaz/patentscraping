
$(document).ready(function () {
    var chartInstance = null;

    // Show and hide loader functions
    function showLoader() {
        $('#loader').addClass('visible');
    }

    function hideLoader() {
        $('#loader').removeClass('visible');
    }

    // Show and hide chart container
    function showChartContainer() {
        $('#keywordChartContainer').removeClass('d-none');
    }

    function hideChartContainer() {
        $('#keywordChartContainer').addClass('d-none');
    }
    function startCreationChart(data) {
        const keywordUsageByYear = {};

        data.forEach(item => {
            const year = item.PublishDate.split('.')[2];
            const keywords = typeof item.Keywords === 'string' ? item.Keywords.split(', ') : []; // Ensure Keywords is a string

            if (!keywordUsageByYear[year]) {
                keywordUsageByYear[year] = {};
            }

            keywords.forEach(keyword => {
                if (!keywordUsageByYear[year][keyword]) {
                    keywordUsageByYear[year][keyword] = 1;
                } else {
                    keywordUsageByYear[year][keyword]++;
                }
            });
        });

        const years = Object.keys(keywordUsageByYear);
        const keywords = Array.from(new Set(years.flatMap(year => Object.keys(keywordUsageByYear[year]))));

        const keywordData = keywords.map(keyword => ({
            label: keyword,
            data: years.map(year => keywordUsageByYear[year][keyword] || 0),
            borderColor: '#' + Math.floor(Math.random() * 16777215).toString(16),
            fill: false,
            hidden: false // All datasets initially visible
        }));

        const chartData = {
            labels: years,
            datasets: keywordData
        };

        if (keywordData.length > 0) {
            renderChart(chartData, data);
            saveChartData(chartData);
            showChartContainer(); // Show chart if there is data
        } else {
            hideChartContainer(); // Hide chart if no data found
        }
    }
    // Create card function
    function createCard(patent) {
        var card = $('<div class="card mb-4">');
        var cardBody = $('<div class="card-body">');
        var cardTitle = $('<h5 class="card-title">').text(`${patent.Title}`);

        // Technologies section
        if (patent.Technologies.length > 0) {
            var techList = $('<ul>');
            patent.Technologies.forEach(tech => {
                var techItem = $('<li class="white-text">').text(`${tech.TechnologyTitle}: ${tech.TechnologyDescription}`);
                techList.append(techItem);
            });
            var techSection = $('<div>').append('<h4>Teknolojiler:</h4>', techList);
            cardBody.append(techSection);
        }

        // Techniques section
        if (patent.Techniques.length > 0) {
            var techniqueList = $('<ul>');
            patent.Techniques.forEach(tech => {
                var techItem = $('<li class="white-text">').text(`${tech.TechniquesTitle}: ${tech.TechniquesDescription}`);
                techniqueList.append(techItem);
            });
            var techniqueSection = $('<div>').append('<h4>Teknikler:</h4>', techniqueList);
            cardBody.append(techniqueSection);
        }

        var cardLink = $('<a class="card-link" href="' + patent.Link + '" target="_blank">').text("Patente Git");
        var cardDetailLink = $('<a class="card-link detay-link" href="/detay/' + patent.No + '">').text("Detay");

        cardBody.prepend(cardTitle); // Adds card title
        cardBody.append(cardLink, cardDetailLink); // Adds links
        card.append(cardBody);
        return card;
    }

    // Save chart data to localStorage
    function saveChartData(data) {
        localStorage.setItem('chartData', JSON.stringify(data));
    }

    // Load chart data from localStorage
    function loadChartData() {
        const data = localStorage.getItem('chartData');

        return data ? JSON.parse(data) : null;
    }
    function loadPatentsData() {
        const patents = localStorage.getItem('patents')
        return patents ? JSON.parse(patents) : null;
    }

    // Render chart with given data
    function renderChart(data, patents) {
        const ctx = document.getElementById('keywordChart').getContext('2d');

        // Destroy previous chart instance if it exists
        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            stepSize: 1 // Y ekseni aralıkları her zaman 1 birimlik olacak
                        }
                    }
                },
                plugins: {
                    legend: {

                        display: true,
                        onClick: (e, legendItem) => {
                            window.location.href = `/legendItem?keyword=${encodeURIComponent(legendItem.text)}`;
                        }
                    }
                }
            }
        });
    }

    // Form submit event
    $('#simpleSearchForm').submit(function (e) {
        e.preventDefault();

        var searchText = $('#simpleSearchInput').val();
        if (!searchText) {
            alert('Lütfen bir değer girin.');
            return;
        }

        showLoader();

        $.post('/search', { searchText: searchText }, function (data) {
            var cardContainer = $('.card-columns');
            cardContainer.empty();
            localStorage.setItem("patents", JSON.stringify(data));
            if (data && data.length > 0) {
                data.forEach(patent => {
                    var card = createCard(patent);
                    cardContainer.append(card);
                });
            } else {
                cardContainer.append('<p class="alert alert-warning" role="alert">Veri bulunamadı.</p>');
                hideChartContainer(); // Hide chart if no data found
            }

            startCreationChart(data);

            hideLoader();
        }).fail(function () {
            var cardContainer = $('.card-columns');
            cardContainer.empty();
            cardContainer.append('<p class="alert alert-danger" role="alert">Veri getirilemedi.</p>');

            hideLoader();
            hideChartContainer(); // Hide chart on failure
        });
    });

    // Submit the form when Enter key is pressed
    $('#simpleSearchInput').keypress(function (e) {
        if (e.which == 13) {
            $('#simpleSearchForm').submit();
        }
    });

    $('#advancedSearchForm').submit(function (e) {
        e.preventDefault();

        var searchText = $('#advancedSearchTitleInput').val();
        var summaryText = $('#advancedSummaryInput').val();
        var startDate = $('#advancedStartDateInput').val();
        var endDate = $('#advancedEndDateInput').val();

        showLoader();

        $.post('/advanced-search', {
            searchText: searchText,
            summaryText: summaryText,
            startDate: startDate,
            endDate: endDate
        }, function (data) {
            var cardContainer = $('.card-columns');
            cardContainer.empty();

            if (data && data.length > 0) {
                data.forEach(patent => {
                    var card = createCard(patent);
                    cardContainer.append(card);
                });
            } else {
                cardContainer.append('<p class="alert alert-warning" role="alert">Veri bulunamadı.</p>');
                hideChartContainer(); // Hide chart if no data found
            }

            startCreationChart(data);
            hideLoader();
        }).fail(function () {
            var cardContainer = $('.card-columns');
            cardContainer.empty();
            cardContainer.append('<p class="alert alert-danger" role="alert">Veri getirilemedi.</p>');

            hideLoader();
            hideChartContainer(); // Hide chart on failure
        });
    });

    $('#advancedSearchForm input').keypress(function (e) {
        if (e.which == 13) {
            $('#advancedSearchForm').submit();
        }
    });

    // Check if the page was reloaded
    if (performance.navigation.type === performance.navigation.TYPE_RELOAD) {
        // Page was reloaded, clear localStorage and card container
        localStorage.removeItem('chartData');
        localStorage.removeItem('patents');
        $('.card-columns').empty(); // Clear the card container
        hideChartContainer(); // Hide chart container
    } else {
        // Page was not reloaded, load chart data and render chart
        const savedChartData = loadChartData();
        const savedPatentsData = loadPatentsData();
        if (savedChartData && savedChartData.datasets.length > 0) {
            renderChart(savedChartData, savedPatentsData);
            showChartContainer();
        } else {
            hideChartContainer();
        }
    }

    // Set a flag in sessionStorage to indicate that the page has been loaded
    sessionStorage.setItem('pageLoaded', 'true');
     $(document).on('click', '.detay-link', function () {
        showLoader();
    });
});
