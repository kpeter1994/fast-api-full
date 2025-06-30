# FastAPI Tutorial


Tutorial video: https://www.youtube.com/watch?v=7DQEQPlBNVM&list=PLEt8Tae2spYnHy378vMlPH--87cfeh33P&index=2&ab_channel=SsaliJonathan

    pip freeze > requirements.txt

Indítás
```
fastapi dev
```

vagy
```
fastapi dev main.py
```

## Adatbázis

```
pip install asyncpg
```

```
pip install pydantic-settings
```

```
pip install sqlmodel
```


## Alembic
```
pip install alombic
alembic init -t async crud/migrations
alembic upgrade head
```

## Adatbázis frissítés

```alembic revision --autogenerate -m "message"```