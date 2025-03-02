from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://neondb_owner:npg_wAPfeFY32VGQ@ep-sweet-meadow-a5fdw1lp-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS todos (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        completed BOOLEAN DEFAULT FALSE
    )
''')
conn.commit()

@app.route('/todos', methods=['GET'])
def get_todos():
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    return jsonify([{"id": row[0], "title": row[1], "completed": row[2]} for row in todos])

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    cursor.execute("INSERT INTO todos (title, completed) VALUES (%s, %s) RETURNING id", (data['title'], data.get('completed', False)))
    todo_id = cursor.fetchone()[0]
    conn.commit()
    return jsonify({"id": todo_id, "title": data['title'], "completed": data.get('completed', False)}), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    cursor.execute("UPDATE todos SET title=%s, completed=%s WHERE id=%s", (data['title'], data['completed'], todo_id))
    conn.commit()
    return jsonify({"id": todo_id, "title": data['title'], "completed": data['completed']})

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    cursor.execute("DELETE FROM todos WHERE id=%s", (todo_id,))
    conn.commit()
    return jsonify({"message": "Deleted successfully"})

# Expose `app` for Vercel
def handler(event, context):
    return app(event, context)
