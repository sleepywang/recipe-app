import os
import logging
import openai
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, current_app
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Explicitly load .env file from the same directory as app.py
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Configuration
DEBUG = True

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__)

# Basic logging configuration
logging.basicConfig(level=logging.INFO)

# Database Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'recipes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')

db = SQLAlchemy(app)

# Enable CORS
CORS(app, resources={r'/api/*': {'origins': '*'}})

# --- Database Models ---

# Association Table for Recipe and Tag
recipe_tags = db.Table('recipe_tags',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    tags = db.relationship('Tag', secondary=recipe_tags, lazy='subquery',
        backref=db.backref('recipes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'tags': [tag.to_dict() for tag in self.tags]
        }

# --- Helper Functions ---

def handle_tags(tags_string):
    """Handles creation and association of tags for a recipe."""
    if not tags_string:
        return []
    
    # Replace Chinese comma with English comma, then split
    processed_string = tags_string.replace('，', ',')
    tag_names = [name.strip() for name in processed_string.split(',') if name.strip()]
    
    tags = []
    for name in tag_names:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        tags.append(tag)
    return tags

# --- API Routes ---

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    return jsonify([recipe.to_dict() for recipe in recipes])

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        new_recipe = Recipe(
            title=data['title'],
            description=data['description'],
            image_url=data.get('image_url')
        )

        new_recipe.tags = handle_tags(data.get('tags'))

        db.session.add(new_recipe)
        db.session.commit()

        return jsonify(new_recipe.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"Error creating recipe: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/recipes/<int:id>', methods=['GET'])
def get_recipe(id):
    recipe = db.session.get(Recipe, id)
    if recipe is None:
        return jsonify({'error': 'Recipe not found'}), 404
    return jsonify(recipe.to_dict())

@app.route('/api/recipes/<int:id>', methods=['PUT'])
def update_recipe(id):
    try:
        recipe = db.session.get(Recipe, id)
        if recipe is None:
            return jsonify({'error': 'Recipe not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        recipe.title = data.get('title', recipe.title)
        recipe.description = data.get('description', recipe.description)
        recipe.image_url = data.get('image_url', recipe.image_url)
        if 'tags' in data:
            recipe.tags = handle_tags(data.get('tags'))
        
        db.session.commit()
        return jsonify(recipe.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error updating recipe {id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/recipes/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    recipe = db.session.get(Recipe, id)
    if recipe is None:
        return jsonify({'error': 'Recipe not found'}), 404

    tags_to_check = list(recipe.tags)

    db.session.delete(recipe)
    db.session.commit()

    if tags_to_check:
        for tag in tags_to_check:
            if not tag.recipes:
                db.session.delete(tag)
        db.session.commit()

    return jsonify({'message': 'Recipe deleted successfully'}), 200

@app.route('/api/ai-suggest', methods=['GET'])
def ai_suggest():
    title = request.args.get('title')
    if not title:
        return jsonify({'error': 'Title parameter is required'}), 400

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        current_app.logger.error("OPENAI_API_KEY is not set in the environment.")
        return jsonify({'error': 'AI service is not configured on the server.'}), 500

    try:
        openai.api_key = api_key
        
        prompt = f"请为 '{title}' 这道菜生成一份详细的烹饪步骤。请直接以编号列表的形式给出步骤 (例如：1. ..., 2. ...)，语言清晰简洁，不要包含食材列表或任何额外的前言或结语。"

        chat_completion = openai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
        )
        
        ai_description = chat_completion.choices[0].message.content

        return jsonify({
            'description': ai_description
        })

    except Exception as e:
        current_app.logger.error(f"AI suggestion failed: {e}")
        return jsonify({'error': 'An error occurred while getting AI suggestions.'}), 500

@app.route('/api/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    return jsonify([tag.to_dict() for tag in tags])

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_url = f"/uploads/{filename}"
        return jsonify({'image_url': file_url})

# Static file serving for uploads
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Command to create database tables
@app.cli.command('init-db')
def init_db_command():
    """Creates the database tables."""
    with app.app_context():
        db.create_all()
    print('Initialized the database.')

if __name__ == '__main__''':
    app.logger.info("Starting Flask development server")
    app.run(debug=True)