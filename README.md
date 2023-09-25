# ocpp-csms (Python/FastAPI/Vue3)

## The application for monitoring and controlling electric vehicle chargers.

### The whole development process [on my YouTube channel](https://www.youtube.com/@user-ni4vw6yw8b/videos)

### Terms

    -  "charge point node" the same as the "charge point service" on the screen
    -  "manager" the same as the "management system" on the screen
    -  "events" are the messages from the "charge point node" to the "manager"
    -  "tasks" are the messages from the "manager" to the "charge point node"

### How does it work

#### Operations initialized by physical charging station

    -  "charge point node" accepts connection from the physical charging station
    -  "charge point node" accepts data from the physical charging station
    -  "charge point node" prepares an "event" and puts it into the queue (see the screen)
    -  "manager" consumes data and handle it as an "event"
    -  "manager" has a monopoly access to the database
    -  after an "event" has handled, the "manager" prepares "task" and puts it into the queue
    -  "charge point node" consumes "task" and executes the one (replies to the physical charging station)

#### Operations initialized by UI

    -  "manager" accepts request from the UI
    -  "manager" prepares "task" and puts it into the queue
    -  "charge point node" consumes "task" and executes the one (sends data to the physical charging station)

Also, explained [in the video](https://www.youtube.com/watch?v=CLE70pABi_U&ab_channel=%D0%94%D0%B5%D0%BD%D0%B8%D1%813)

In the context of the client-server architecture, the csms is a server, the charging station is a client.
The physical charging station establishes websocket connection and interacts with the management system.

The server consists of two parts: charge point service and management system.
The responsibility of the charge point service is the direct interaction with physical charging stations.

The responsibility of the management system is the business logic (such as permissions, charging process control,
payments, etc).
It knows nothing about how the charge point service works.

Both parts interact with each other through the queue and durable AMQP protocol.
The advantage of the approach is high scalability. Say, we have a few hundred physical charging stations.
It would be pretty complex and expensive to serve so many connections by a single server.
We would want to have a way to scale the application and scale without rebooting. With the provided approach,  
you will be able to set up as many charge point services as we need depending on the network load, and the management
system won't know
anything about it and will work in a standard mode.

Example: say we have an operation initiated by a physical charging station as an event.
Charge point service accepts data, prepares event, and puts it into the queue. The management system accepts it,
takes the decision on how to process a given event (regarding predefined conditions and database state), prepares a
reply as a task
, and puts data into the queue. All existing charge point services consume tasks, check if the charge point, specified
in the task,
is connected to the host and if so, executes the task or just sends data to the physical charging station.
And vice versa with operations initiated by UI. The user sends data into the management system. The system prepares data
as a task and puts it into the queue. All charge point services consume the task and further actions happen
as described before.

Stack: python3.11, FastAPI, Rabbitmq, Postgresql, Sqlachemy, MongoDB, Docker, Docker-Compose, Vue3/Vuetify3.

