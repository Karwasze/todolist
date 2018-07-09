# Todolist

Todolist application implemented using Flask and SQLite3.


## Getting Started

### Prerequisites

Required modules are listed in requirements.txt

## Usage

### Setting up application

```console
$ export FLASK_APP=todolist.py
$ flask run
```

### Getting list of entries

Our todolist view is under /todolist address.
It has two HTML methods, GET and POST.
Depending on the method used, it either shows us our todolist (GET),
or returns JSON with task ID associated with given title and status.
In our case, we want to use the GET method.

### Getting ID of given task

When using a POST method with a valid JSON it returns 
another JSON with our task ID, eg. when given
```
{
	"title": "Conquer the world",
	"done": false
}
```
returns
```
{
	"task_id": 5
}
```

### Patching entries

We can also patch entries. To do that, we have to
access /todolist/<id_of_task> address with a PATCH method,
and of course JSON with values we want to patch. Eg.
```
PATCH '/todolist/2'
{
	"done":true
}
```
changes the value of second entry to "done".

### Getting metadata

We can also access metadata associated with given entry
using /todolist/<id_of_task> with GET method. It returns JSON
containing title, status, ip of author, and creation date
(example below)
```
{
 "title": "Learn even more Python",
 "done": false,
 "author_ip": "123.45.67.89",
 "created_date": "2018-05-08 10:00:00",
}
```
### Googling

We can also google things from our website using
`/google?co=foobar` view, where foobar is our
query. It redirects to google and searches for our query.
