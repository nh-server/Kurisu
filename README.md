# Kurisu

A Discord server bot developed for [Nintendo Homebrew on Discord](https://discord.gg/C29hYvh). Maintained primarily by NH staff and helpers.

Although it is open source, this bot is not really designed to be used in other setups at the moment; the source is mainly just available for those interested in how it works on the Nintendo Homebrew server.

## Server template

A server template is available for testing Kurisu, with all the channels and roles necessary.

* https://discord.new/hyTjkbQAbhWr

## Setting up for local testing in Docker (recommended)

To test changes to Kurisu locally using Docker, make sure Docker Desktop (Windows and macOS) or Docker Engine (Linux) is installed. If you are using Windows, it's heavily recommended to use Powershell so the commands shown here run as intended.

* [Get Docker | Docker Documentation](https://docs.docker.com/get-docker/)

For Linux, docker-compose must be installed separately.

* [Install Docker Compose | Docker Documentation](https://docs.docker.com/compose/install/)

Create a new application on Discord and add a bot. Put the token in `token.txt` in the same directory. (Newline at the end of the file doesn't matter.)

* [Discord Developer Portal](https://discord.com/developers/applications)

The file `server_logs_url.txt` is the url to a database of a different project, which is used along Kurisu in production. For local testing purposes, this file still needs to be created but can be blank, in which case the `server_logs` cog won't be loaded.

Set up the database volume with the following commands, this can also be used in cases in which the schema was updated and the database volume still contains an old version, missing tables necessary to run the bot. This will pull postgres:13 to run as the database, create the tables (removing them if they already exist) then stop and remove the container. 
```
docker-compose up --build -d db
cat ./schema.sql | docker compose exec -T db psql -U kurisu -d kurisu
docker-compose down db
```

Start Kurisu with the following command. Assuming a clean setup, this will pull postgres:13 to run as the database, and python:3.9-alpine as the base image for Kurisu, then build a new Kurisu image. Then it will start up postgres first, then kurisu once the database is active.

```
docker-compose up --build
```

postgres database files are stored in a Docker volume called `kurisutestdb`. Use Ctrl-C if not running in detached mode to stop the bot.
* [Use volumes | Docker Documentation](https://docs.docker.com/storage/volumes/)

### Other useful commands

* `docker-compose build` - Build only, pull base images if required

* `docker-compose build --pull` - Build only, always try to pull base images for newer versions

* `docker-compose pull` - Pull images, in this case update postgres:13

* `docker-compose up -d` - Detach and run containers in the background

* `docker-compose down` - Stop running containers and remove them

## Set up for local testing manually

* Ever since the move to Docker and PostgreSQL this has not been as well tested, so tell us if something is wrong or confusing!

Set up PostgreSQL 13 or later (older versions aren't tested but might work).

Python 3.9 or later is required.

Install the dependencies in `requirements.txt`, ideally in a virtual environment.

Create a new application on Discord and add a bot.

- [Discord Developer Portal](https://discord.com/developers/applications)

Inside `data/`, create `config.ini` with the contents:

```ini
[Main]
token = <token for Discord bot>
database_url = <url of the database>
server_logs_url = <url to server logs database`
```

`database_url` and `server_logs_url` should follow a format like `postgresql://user:password@ipaddr/database` (example: `postgresql://kurisu:dev123@127.0.0.1/kurisu`). `server_logs_url` can be left blank.

Run the bot:

```
python3 kurisu.py
```
