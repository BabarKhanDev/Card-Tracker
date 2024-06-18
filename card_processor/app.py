import os

from flask import Flask, request, render_template, redirect, Response
from flask_cors import CORS
from PIL import Image

from common.config import load_database_config, load_tcg_api_key
from common.database import connect

# Connect to database and tcg API
config = load_database_config("config.ini")
conn = connect(config)
tcg_api_key = load_tcg_api_key("config.ini")

# Set up flask
app = Flask(__name__)
CORS(app)

# TODO Endpoint: card -> []card_id