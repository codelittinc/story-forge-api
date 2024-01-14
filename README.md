# Story Forge API

## Overview

StoryForge is an API that allows a developer to plug and play a knowledge management API into any application. 

## Integrations

It uses [OpenAI](https://openai.com/) as the LLM, [Box](https://box.com) as the file management service and [MongoDB](https://www.mongodb.com) as both the database and the Vector Search.

## Features

- **File Management**: Upload, store, and delete files with associated metadata.
- **Task Execution**: Submit tasks for NLP processing with callbacks upon completion.
- **Database Querying**: Execute and manage queries against a PostgreSQL database.
- **Swagger Documentation**: Interactive API documentation and testing interface.

## Prerequisites

To run this application, ensure you have the following installed:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## How to run

The easiest way is through the usage of docker-compose. From within the project folder run: 

```
sh bin/dev
```

It will run the docker-compose.yml and enter you into the container. Once inside it run:

```
python app.py
```

By accessing http://localhost:8080 you'll see the docs.
