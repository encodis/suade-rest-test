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
http://127.0.0.1:5000/summary/2019-08-01
```

Results are returned as a JSON formatted string:

```
{
    "items": 2895,
    "customers": 9,
    "total_discount_amount": 15152814.736907527,
    "discount_rate_avg": 0.4457418957252218,
    "order_total_avg": 15895179.735734595,
    "commissions": {
        "total": 914342.3436,
        "order_average": 2627697.374617506,
        "promotions": {
            "2": 2686420,
            "5": 8602640
        }
    }
}
```

Using an invalid (i.e. incorrectly formatted) date will return the string `Invalid date`. Dates that are valid but that are outside the range of dates held within the database will return 0 for all entries in the summary.


## Structure

The main bulk of the code is in the `queries.py` module. This sets up a database connection in the correct application context and defines a number of queries against it. The application module (`endpoint.py`) is quite short and simply sets up the correct routing for the application and runs the appropriate query function.

## Testing

Time constraints preclude the development of more extensive testing. Sample tests are in `test_queries.py` which currently just test date validation. Run the tests using [pytest](https://docs.pytest.org/en/stable/contents.html):

```
$ pytest
```

Ideally the database queries themselves would be tested but this would require, for example, a test database to be created (with known values) and the query functions suitably mocked. (This is because the database is not created by the app and populated as it is used---it is, in this example at least, a more external entity.)

