FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8050
ENV IS_DEBUG False
CMD ["python", "main.py"]