# Lexcaliber

Lexcaliber is an ongoing project to develop novel algorithms and analysis techniques for legal research.

Our current efforts include:
- Designing and assessing various recommendation algorithms to surface relevant court cases given a set of cases or textual content.
  - Building a search function for caselaw that marshals both textual content of the user's query and previously-identified relevant cases to display the most relevant results to the user.
- Scraping and analyzing [parentheticals](https://www.law.georgetown.edu/wp-content/uploads/2018/07/Parentheticals-Bluebook-Handout-Revision-Karl-Bock-2016.pdf) of legal citations to infer semantic content and relevance of cases to one other.
- Utilizing [graph embedding](https://en.wikipedia.org/wiki/Knowledge_graph_embedding) techniques to efficiently deliver recommendations and create intuitive visualizations.
- Empirically determining the degree of reliance on precedent  courts demonstrate in different jurisdictions and areas of the law by estimating the "predictability" of citation behavior.
- Designing a web interface that can be used by legal researchers to quickly discover and identify relevant caselaw using our systems.

See [Eksombatchai et. al (2017)](https://arxiv.org/abs/1711.07601), [Huang et. al (2021)](https://arxiv.org/abs/2106.10776), [Sun et. al (2016)](https://arxiv.org/pdf/1610.02906.pdf) for literature that informs our current approaches

Our current work is focused on the federal appellate corpus (all circuit courts as well as the Supreme Court), with the aim of building systems that generalize to other jurisdictions.

This repository contains the bulk of the logic and infrastructure powering this project, as well as command-line and REST interfaces. See [scotus-explorer](https://github.com/lexcaliber/scotus-explorer) for more information about the prototype web interface we're building to demonstrate the technology.


## Getting set up

1. Set PROJECT_PATH to the github directory, using .env or standard bashrc
2. Set a psql server hostname, port, and username + password if necessary in .env (making sure you create the empty database)
3. To set up the database schema, `alembic upgrade head`. Make sure you have a username in .env.
4. To install the CLI, run in the main project directory: `pip install --editable .` Run `lxc --help` for a list of all commands.
5. To populate your database with data from CourtListener, run `lxc data download` with your desired jurisdictions.
6. To run the API server: `lxc server run`

## Migrations
- Run `alembic upgrade head` if your database schema is out of date.

![A visualization of the most important cases in Roe v. Wade's egonet](output/ego-plot.png)

![4000 important SCOTUS cases by RolX classification](output/important-cases-plot.png)
