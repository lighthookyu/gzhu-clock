FROM python

EXPOSE 5000

WORKDIR /code
ADD . /code

RUN pip install -r requirements.txt --target=./

ENTRYPOINT [ "" ]

CMD python app.py
