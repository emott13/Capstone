import psycopg2
from faker import Faker
fake = Faker()

conn = psycopg2.connect(database="Capstone", user="postgres", password="cset155", host="localhost", port="5432")
print("Database connection successful")
cur = conn.cursor()

for i in range(10):
    username = fake.user_name()
    firstName = fake.first_name()
    lastName = fake.last_name()
    email = fake.email()
    password = "password"
    dob = fake.date_of_birth()
    phone = fake.phone_number()
    cur.execute("INSERT INTO users(username, first_name, last_name, email, password, dob, phone, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, now())", (username, firstName, lastName, email, password, dob, phone))
