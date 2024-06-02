class Patent {
    constructor({ No, Title, Summary, Link, Technologies, Techniques, PublishDate, Keywords }) {
        this.No = No;
        this.Title = Title;
        this.Summary = Summary;
        this.Link = Link;
        this.Technologies = Technologies;
        this.Techniques = Techniques;
        this.PublishDate = PublishDate;
        this.Keywords = Keywords;
    }
}

module.exports = { Patent };
