# SCOTUS Network Analysis

This repository contains various files, databases, and scripts relating to an ongoing effort to empirically analyze 
Supreme Court precedent with a graph theoretic approach.

![A visualization of the most important cases in Roe v. Wade's egonet](output/ego-plot.png)

![Barnette](output/ego-plot-West%20Virginia%20Bd.%20of%20Ed..png)

![Obergefell](output/ego-plot-Obergefell.png)

![4000 important SCOTUS cases by RolX classification](output/important-cases-plot.png)

## Running the Server

1. Set PROJECT_PATH to the github directory, using .env or standard bashrc
2. Set a psql server hostname, port, and username + password if necessary in .env
3. `flask run`

## Migrations

Look at ./db/migrations and just `python <migration>.py`
