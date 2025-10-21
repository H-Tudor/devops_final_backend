# Devops Final Backend - LLM Compose Generator

Transform a loose list of services in a full docker compose file with the power of AI

## About

This is a FastAPI-based API that allows the generation of docker compose files based
on a list of desired services and other configuration parameters.

This application is intended to be used by external client services instead of directly by
human users allowing a degree of extensibility, but at the same time it is a
Proof-of-Concept, suitable for small scale use

As a Proof-of-Concept, the application does not have certain features like
- a database for its own state (like tracking consumption of tokens by client services)
- a queue of llm-requests that are processed based on availability
- a cache of previous generation
- request rate limitting

In order to controll access to this application, all LLM generation endpoints are guarded
by a bearer token authentification, the token being provided and checked by a keycloak
instance. Each client service will have a user / password account in the app's realm
in keycloak and the tokens generated are short lived (default 5 minutes) with the option
to refresh them.

In terms of the LLM models used, the app can be configured via the environment file to use
any model of any provider supported by LangChain (v0.3)

The application API documentation can be accessed while not in production at `/docs/` endpoint.

## Setup

This application requires a keycloak instance for authentification of client services,
and the keycloak shoul have a realm with
- a confidential client setup for direct access
- a user with password for each client service (frontend) that will be using the API

### 1. Install Dependencies

```sh
uv sync
```

or

```sh
uv venv
uv pip install r requirements.txt
```

### 2. Environment File

Use the template file called `.env.example` to create `.env` and populate it with the appropiate values.
Apply the same for the `env.keycloak.example` used for the docker compose container env

## Commands

Running the application

```sh
uv run devops-final-backend
```

For a more commands, check the [usefull comands file](./usefull_commands.sh)

## Testing

Run the unit & integration tests using the following command:

```sh
uv pytest
```

The API is tested using schemathesis and during testing it requires an available keycloak instance
and configured in settings a test_username and test_password

## Developer Notes

### PreCommit Strategy

This repository is configured with a precommit configuration comprised of the following stages:

Generic precommit checks:
- trim trailing whitespace
- fix end of files
- check yaml
- check for added large files

Code linting using
- ruff check & format
- mypy
- pylint

These linter cover not just the code but typing and docs too, thus ensuring the developer has documented their code.

Automation of manual actions
- running the unit tests using pytest, to ensure that when commiting a code change it is atomically functional
- clearing the caches
- exporting the requirements file if packages changed
- building the documentation

As a developer, in order to prevent commit failures, you should manually run these checks before commiting the code using

```sh
uv run pre-commit run --all-files
```
