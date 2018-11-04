# Save Email Data from JSON to Postgres

## Dependencies

* Python 3
* Postgresql 
* Psycopg2

Create a postgresql db and user, then edit the psycopg2 connect function with the new details. Running the script from the terminal will create tables and insert the data. Ensure the json file is in the same directory.


# Storing Currency Rates

## Dependencies

* Python 3.6
* Postgresql
* Psycopg2
* Requests

## Deploying

Clone application code to the server and add database name, user and host as environment variables.

* Run the database.py file to create the database table.

Use crontab -e command to create a new crontab file and add the following line to execute the task every weekday at 9am:

```0 9 * * 1-5 [replace with server python path] [path to file]/rates.py```

## Monitoring

Best approach is configuring proper logging with something like Sentry. For the challenge, adding the following line to the crontab file, would allow you to receive an email notification on error:

```MAILTO=[email address]```
