## Introduction
The goal of this project is to facilitate the coordination between several *users* in carrying out some *tasks*. It is deliberately abstract: No assumptions are made about the nature of the tasks themselves. The original use case was to make a large number of sequential API calls, and it was necessary to keep track of how far along are we, and who is currently making the calls.

## Details
### Components
A task could be anything. It has a name, a description, a *data* field, and a queue of users who *volunteered* to run the task. A task can be ran by precisely one user at a time, and only the runner can modify the data field, though it is publicly accessible. A user can run a number of tasks at a time, and must make a request to a specific API endpoint every N seconds to assert that they are still running the task. This is a "maintain" message.
A task is considered idle if it has no runner, or if no "maintain" messsage has been received for a while. In this case, the supervisor looks for the first person in line and notifies them. The message is sent through an API request as well: Each user must also host a server to process messages from the supervisor.

### Limitations
It is assumed that there is a small number of tasks, and that security is not a concern (e.g., the supervisor server is hosted locally).
