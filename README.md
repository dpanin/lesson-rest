# Lesson REST service for Stepik

Simple REST service which uses Stepik REST API to get id of steps.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites & installing

* Python 3.5+
* aiohttp
* aiocache

Install required packages using pip:
```
pip install -r requirement.txt
```

### Running

To run this app on your local machine for testing purposes just run app.py file:

```
python3 app.py
```

If you want to run this app on server, change IP in app.py file:

```python3
web.run_app(app, host='0.0.0.0', port=8080)
```

## Request & Response Examples

### GET /lessons=[lesson_id]

Example: http://127.0.0.1:8080/lesson=1

Response body:

```json
[
    541,
    1053,
    92,
    4,
    443
]
```

## Built With

* [aiohttp](https://github.com/aio-libs/aiohttp/) - Asynchronous HTTP Client/Server
* [aiocache](https://github.com/argaen/aiocache) - Asyncio cache framework for redis, memcached and memory 


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details