import yfinance as yf
from supabase import create_client, Client
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import os
import psycopg2
from bulk_upload import bulk_upload
