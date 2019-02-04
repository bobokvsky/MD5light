# MD5 light
`MD5light` is a small shell and web service for computing `MD5` of a file on the Internet.
(Test task for BostonGene.)

## Installation
1. Install project dependencies
```shell
pip install cmd2
pip install requests
```

2. Launch `md5light.py`.

## Usage
### Shell usage
Launch `md5light.py`:
```shell
>>> python md5light.py
Welcome to the MD5Light! Type help or ? to list commands.

>>> (MD5Light) ...
```

##### Available commands:
`add <url> (--email <email>)`  - add task to count md5 hash of file from `<url>`. If email is specified and SMTD session is active, the task will send email with results. 
```shell
>>> (MD5Light) add https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg --email to@example.com
{'id': 'ea602320-49c7-4df9-82c5-603f018da9d1'}
```

`get <id>`  - get status and results of task with `id`.
```shell
>>> (MD5Light) get ea602320-49c7-4df9-82c5-603f018da9d1
{'url': 'https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg', 'md5': None, 'status': 'running'}
>>> (MD5Light) get ea602320-49c7-4df9-82c5-603f018da9d1
{'url': 'https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg', 'md5': 'c8e7e1fc344be6982710f54d47191ef6', 'status': 'done', 'status_code': 200}
```

`getall`  - get all ids of tasks.
```shell
>>> (MD5Light) getall
['ea602320-49c7-4df9-82c5-603f018da9d1']
```

`run`  - run a simple server based on `http.server.BaseHTTPRequestHandler`. Its url is http://localhost:8000. The log of servers is writing to `log_messages_server.txt`.
```shell
>>> (MD5Light) run
Server run.
>>> (MD5Light) run
Server is already running.
```

`shutdown`  - shutdown the server.
```shell
>>> (MD5Light) shutdown
Server shut down.
>>> (MD5Light) shutdown
Server is already shut down.
```

`startSMTP` - Start SMTP session for sending emails. Note that `MD5light` uses only port `587` for SMTP (TCP session). If accepted, then the command `add` with specified email will send mail.
```shell
>>> (MD5Light) startSMTP
Print following:
>>> SMTP server host: smtp.gmail.com
>>> Username: <your username>
>>> Password: <your password>
>>> Your email: <your email>
(235, b'2.7.0 Accepted')
```

`quitSMTP` - Stop SMTP session.
```shell
>>> (MD5Light) quitSMTP
Quiting from SMTP session...
Done.
>>> (MD5Light) quitSMTP
SMTP session is not turned on.
```

`quit` - Quit from shell. This will turn off server and stop SMTP session.
```shell
>>> (MD5Light) quit
Shutdowning the server...
Server shut down.
Quiting from SMTP session...
Done.
>>> (base shell) ...
```

### GET and POST usage
When the server in running from shell by command `run`, you can use `GET` and `POST` requests to the server from the other console.

#### POST to create a task
(Note that the mail will be sent when SMTP session is active.)
```shell
>>> curl -X POST -d "email=user@example.com&url=https://speed.hetzner.de/100MB.bin" http://localhost:8000/submit
{'id': '5a52c0cd-5047-4a44-8ce3-7c8afd2fe807'}
```

#### GET to retrieve task status and md5 hash
(Note that the mail will be sent when SMTP session is active.)
When task is running:
```shell
>>>  curl -X GET http://localhost:8000/check?id=5a52c0cd-5047-4a44-8ce3-7c8afd2fe807
["{'url': 'https://speed.hetzner.de/100MB.bin', 'md5': None, 'status': 'running'}"]
```
When task is done:
```shell
>>>  curl -X GET http://localhost:8000/check?id=5a52c0cd-5047-4a44-8ce3-7c8afd2fe807
["{'url': 'https://speed.hetzner.de/100MB.bin', 'md5': '2f282b84e7e608d5852449ed940bfc51', 'status': 'done', 'status_code': 200}"]
```