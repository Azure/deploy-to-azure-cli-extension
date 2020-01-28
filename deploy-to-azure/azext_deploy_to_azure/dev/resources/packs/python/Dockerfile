FROM python
ENV PORT port_number_place_holder
EXPOSE port_number_place_holder
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python"]
CMD ["app.py"]