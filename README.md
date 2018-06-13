# How to install the project:
Install redis see: https://redis.io/topics/quickstart

```
sudo apt-get install libpq-dev python-dev
python3 setup.py install
```
# Options of the project
```
usage: pyg-bench [-h] --config-file CONFIG_FILE [--slave] [--send-tasks]
                 --interval INTERVAL --title TITLE --threads THREADS

Tests suites for postgresql

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        config file path                  | Required
  --slave               Set type of tasks executions      | Optional (Default False)
  --send-tasks          Set type of tasks executions      | Optional (Default False)
  --interval INTERVAL   Interval tha will run the tests   | Required
  --title TITLE         Title of thet dashboard           | Required
  --threads THREADS     Paralelal Executions              | Required
```

# Example how to run:

## Master
```
--config-file config.ini --title "testing env" --threads 4 --interval 900 --send-tasks
```

## Slave
```
pyg-bench --config-file config.ini --title "testing env" --threads 4 --interval 900 --slave
```

## Slave + sending tasks
```
pyg-bench --config-file config.ini --title "testing env" --threads 4 --interval 900 --slave --send-tasks
```
## Then access your dashboard to see live the execution
```
http://localhost:9111
```
See 
![Pic 1 – Dashboard view](img/dashboard.png?raw=true "Pic 1")