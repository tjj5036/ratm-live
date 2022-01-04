# ratm.live source code
This is the code that backs [ratm.live](http://ratm.live). It is written using a combination of Python ([Flask](https://flask.palletsprojects.com/en/2.0.x/)), [Bootstrap 4](https://getbootstrap.com/), and [PostgreSQL](https://www.postgresql.org/) 


## Prerequisites

1. Download and install PostgreSQL. Any version >= 10 should be fine but this has only been tested on 12 and 14.
2. Configure a `rage_read_only_rl` role in Postgres. This role will be the one we use to connect to the database that has read only access. Be sure to set a strong password!
    * `create role rage_read_only_rl password USE_GOOD_PASSWORD_HERE;`
3. Grant login to `rage_read_only_rl`: 
    * `alter role rage_read_only_rl with login`.
4. Create a `rage` database: 
    * `create database rage`
5. Grant select on that empty database:
    * `grant select on database rage to rage_read_only_rl`.
6. Set the following environment variables in one of `.bashrc`, `.zshrc`, or `.bash_profile` depending on the system or just export them before running Python: 
    * `PGUSER=rage_read_only_rl`
    * `PGPASSWORD=SAME_PASSWORD_ABOVE`
    * `PGDBNAME=rage`
    * `PGPORT=WHATEVER_PORT_POSTGRES_IS_USING`.
7. Setup Python 3 locally. This is system dependent.

## Getting Started

1. Contact [me](ratm.live@gmail.com) for a database dump file. I'll add an example SQL file in a future commit so this step won't be necessary.
2. Load the database file into the database you just created:
    * `psql -d rage < database_dump.sql`.
3. Checkout this repo into a directory of your choosing.
4. `cd` to that directory
5. Create a virtual Python environment: 
    * `python3 -m venv venv`
6. Source that `venv`:
    * `source venv/bin/active`
7. Install all the dependencies in the `requirements.txt` file:
    * `pip install -r requirements.txt`
8. Run the application:
    * `python -m flask run -p 4999`
9. Visit the [address it should be running on](http://127.0.0.1:4999/) and verify everything looks good!

## Other Notes:

This uses a simple MVT approach to render everything.
I already stare at a screen 50+ hours a week so unless things were dead simple the project wasn't getting off the ground.
I'd love to make things more interactive and to give things a more "modern" feel - if you have ideas please get in touch!
Along the same vein in order to get something working quickly I took a few shortcuts.
If you spot anything egregious please file a PR!
