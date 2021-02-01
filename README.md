# suade-rest-test

This repository contains a solution to a technical challenge with the goal:

> To create an endpoint that, for a given date, will return a report that will contain (a number of) metrics

This has been implemented as a Python script run from the command line. 

## Setup & Installation

Clone the repository into a suitable folder:

```
$ git clone https://github.com/encodis/suade-rest-test.git
```

Set up a Python virtual environment using the tool of your choice e.g.

```
$ cd suade-rest-test
$ python3 -m venv env
$ source env/bin/activate
```

Install the requirements:

```
$ python3 -m pip install -r requirements.txt
```

## Usage

First, create the database that will be used:

```
$ python3 -s build_db.py ./data sales.db
```

These values can be changed but the application expects the database to be called `sales.db` in the root directory of the repository. This only needs to be run once.

Now run the Flask application:

```
$ FLASK_APP=endpoint.py python3 -m flask run
```

Default values for the server IP address are used. To query the application issue a request of the form:

```
http://127.0.0.1:5000/summary/2019-09-01
```

Results are returned as a JSON formatted string:

```
{
    "items": 2699,
    "customers": 8,
    "total_discount_amount": 18164159.989283696,
    "discount_rate_avg": 0.5483430441509592,
    "order_total_avg": 17027476.990291964
}
```

Using an invalid date will return the string `Invalid date`. Dates that are valid dates but outside the range of dates held within the database will return 0 for all entries in the summary.

> NOTE: Due to time constraints the data returned does not include the "commission" and "promotion" fields.

## Structure

The main bulk of the code is in the `queries.py` module. This sets up a database connection in the correct application context and defines a number of queries against it. The application module (`endpoint.py`) is quite short and simply sets up the correct routing for the application and runs the appropriate query function.

## Testing

Time constraints preclude the development of more extensive testing. Sample tests are in `test_queries.py` which currently just test date validation. Run the tests using [pytest](https://docs.pytest.org/en/stable/contents.html):

```
$ pytest
```

Ideally the database queries themselves would be tested but this would require, for example, a test database to be created (with known values) and the query functions suitably mocked. (This is because the database is not created by the app and populated as it is used---it is, in this example at least, a more external entity.)

