require('dotenv').config();
const express = require('express');
const axios = require('axios');
const path = require('path');
const cors = require('cors');
const fetch = require('node-fetch');
const bodyParser = require('body-parser');
const { Patent } = require('./model');
const openaimodule = require('openai')
const app = express();
const port = 3008;
const tokenizer = require('gpt-tokenizer');
const pdf = require('pdf-parse');
let patents = [];


const text = 'öğüt '
const tokenLimit = 16385;

// Encode text into tokens


const openaiApiKey = process.env.OPENAI_API_KEY;
const openai = new openaimodule.OpenAI({ apiKey: openaiApiKey })

console.log(openaiApiKey)

app.set('view engine', 'ejs');
app.use(express.static(path.join(__dirname, 'public')));
app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

async function getChatGPTResponse(prompt) {
    try {
        const completion = await openai.chat.completions.create({
            messages: prompt,
            model: "gpt-3.5-turbo",
        });
        const message = completion.choices[0].message.content;
        return message;
    } catch (error) {
        console.error('Error getting response from OpenAI:', error);
        return 'Sorry, something went wrong.';

    }
}

async function fetchAndExtractPDFContent(url) {
    try {
        const response = await axios.get(url, { responseType: 'arraybuffer' });
        const pdfBuffer = response.data;
        const data = await pdf(pdfBuffer);
        return data.text;
    } catch (error) {
        console.error('Error fetching or parsing PDF:', error);
        throw new Error('Failed to fetch or parse PDF');
    }
}

app.post('/chat', async (req, res) => {
    const userMessage = req.body.message;
    const gptResponse = await getChatGPTResponse(userMessage);
    res.json({ response: gptResponse });
});


app.get('/', (req, res) => {
    res.render('index', { patents: patents });
});

app.post('/search', async (req, res) => {
    const searchText = req.body.searchText;
    const encodedQuery = encodeURIComponent(searchText);
    console.log("query: " + encodedQuery);
    patents = await fetchPatents(encodedQuery);
    res.json(patents);
});

app.get('/about', (req, res) => {
    res.render('about');
});
app.get('/legendItem', (req, res) => {
    const keyword = req.query.keyword; // URL'den keyword parametresini al
    const keywordPatents = patents.filter(patent => patent.Keywords.includes(keyword))
    res.render('keywordPage', { keyword: keyword, patents: keywordPatents });
});
app.get('/test', (req, res) => {
    res.render('test');
});

app.post('/advanced-search', async (req, res) => {
    const { searchText, summaryText, startDate, endDate } = req.body;
    const encodedQuery = encodeURIComponent(searchText);
    const encodedSummary = encodeURIComponent(summaryText);
    patents = await advancedFetchPatents(encodedQuery, encodedSummary, startDate, endDate);
    res.json(patents);
});

app.get('/detay/:patentNo', async function (req, res) {
    var patentNo = req.params.patentNo;
    var selectedPatent = patents.find(patent => patent.No === patentNo);
    const pdfExtracted = await fetchAndExtractPDFContent(selectedPatent.Link);
    const withinTokenLimit = tokenizer.isWithinTokenLimit(pdfExtracted, tokenLimit)
    console.log(withinTokenLimit);
    if (withinTokenLimit != false) {
        res.render('detay', { patent: selectedPatent, extractedData: pdfExtracted });

    } else {
        res.render('detay', { patent: selectedPatent, extractedData: selectedPatent.Summary });

    }
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});

async function fetchPatents(query) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/patent?q=${query}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data.map(patentData => {
            const technologies = patentData.Technologies.map(tech => ({ TechnologyTitle: tech.TechnologyTitle, TechnologyDescription: tech.TechnologyDescription }));
            const techniques = patentData.Techniques.map(tech => ({ TechniquesTitle: tech.TechniquesTitle, TechniquesDescription: tech.TechniquesDescription }));
            const cleanSummary = patentData.Summary.replace(patentData.patent_data.title, "");
            return new Patent({
                No: patentData.No,
                Title: patentData.patent_data.title,
                Summary: cleanSummary,
                Link: patentData.Link,
                Technologies: technologies,
                Techniques: techniques,
                PublishDate: patentData.patent_data.publish_date,
                Keywords: patentData.Keywords,
            });
        });
    } catch (error) {
        console.error('Hata:', error);
        return [];
    }
}

async function advancedFetchPatents(query, words, startDate, endDate) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/patent?q=${query}&words=${words}&startDate=${startDate}&endDate=${endDate}`);
        if (!response.ok) {
            throw new Error('Network response was not ok for advance');
        }
        const data = await response.json();
        return data.map(patentData => {
            const technologies = patentData.Technologies.map(tech => ({ TechnologyTitle: tech.TechnologyTitle, TechnologyDescription: tech.TechnologyDescription }));
            const techniques = patentData.Techniques.map(tech => ({ TechniquesTitle: tech.TechniquesTitle, TechniquesDescription: tech.TechniquesDescription }));
            return new Patent({
                No: patentData.No,
                Title: patentData.patent_data.title,
                Summary: patentData.Summary,
                Link: patentData.Link,
                Technologies: technologies,
                Techniques: techniques,
                PublishDate: patentData.patent_data.publish_date,
                Keywords: patentData.Keywords,
            });
        });
    } catch (error) {
        console.error('Hata:', error);
        return [];
    }
}