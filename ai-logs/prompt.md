this repository will contain boilerplate code for a full-stack application

the frontend will be react app
the backend will be written in FASTApi with authentication and authorization set up.

frontend will include a simplisitic login page with proper validation.

create proper folder structure with clear split b/w frontend and backend, ask for confirmation with a propsed folder structure.

the backend will use sqllite for now. but use an adapter for all db access so we can replace it easily.

use code first approach for db

the backend has proper UTs. but add them after I test the functionality.

containerize the front-end and backend applications. 
also create a docker compose file
add readme with podman instructions to run the compose file

there should be a cold-start setup, which provides some data to start with.

    installs two users manager, worker with passwords in reverse of the username, e.g. ynnub for bunny

the data includes products, support-requests(related to products), and sales.

manager can see all records.

worker can only see products and support requests.

manager also sees some interactive charts & searchable tables for:
  - product sales, revenue generated over month/quarter/year.
  - product support-requests, and also some stats like:
        current or past requests:
        average/95p resolution time for completed tasks
        number of requests over month, quarter, year
  - more data visualization you recommend

DO NOT FORGET: This is a simple boilerplate project to get started on such a task, not an end product, so keep it simple and easy for changes in requirements or scaling up later.