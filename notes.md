Requirements:

```python
pip install flask
pip install requests
pip install gunicorn
```

Run daemonized auto-reloading gunicorn server tracked with process ID:

```
gunicorn bananotracker:app -p bananotracker.pid -w 4 --access-logfile gunicorn.log -b 0.0.0.0:8999 -D --reload
pkill gunicorn
```

Reverse proxy to gunicorn:

```
Apache:
ProxyPass / http://localhost:8999/

Caddy:
reverse_proxy localhost:8999
```

Include CSS / JS:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrap.min.css') }}">
<script src="{{ url_for('static', filename='js/jquery-3.6.0.min.js') }}"></script>
```

