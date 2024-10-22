# MusicFlow
## Initialize Project
In `backend`,
```bash
# download packages
pip install django djangorestframework django-cors-headers

# run django server
python manage.py runserver
```
In `frontend`,

```bash
npm install

# start sveltekit server.
npm run dev
```
Access web through sveltekit URL.

## Frontend Build
To create a production version of your app:
```bash
npm run build
```
And use thie to check it:
```
npm run preview
```

## Dependencies Install
To install dependencies:
```
pip install -r requirements.txt
```

## Docker Container:
Build and run:
```
 docker-compose up --build
```

Stop and remove:
```
docker-compose down
```