import feedparser
from flask import Flask, render_template, request
from datetime import datetime, timezone
from operator import attrgetter
import random
app = Flask(__name__)

PREDEFINED_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "http://ep00.epimg.net/rss/tags/noticias_mas_vistas.xml",
    # Añade más feeds predefinidos aquí
]
def get_entry_published(entry):
    if hasattr(entry, 'published_parsed'):
        return entry.published_parsed
    else:
        # Utiliza 'updated_parsed' como respaldo si 'published_parsed' no está disponible
        fallback_date = entry.get('updated_parsed', None)

        # Si no hay fecha disponible, devuelve una fecha muy antigua
        if fallback_date is None:
            return datetime(1, 1, 1, tzinfo=timezone.utc).timetuple()
        else:
            return fallback_date
    
@app.route('/', methods=['GET', 'POST'])
def index():
    feed_url = ''
    entries = []

    if request.method == 'POST':
        feed_url = request.form['feed_url']
        entries = get_feed_entries(feed_url)
    
    predefined_entries = []
    for url in PREDEFINED_FEEDS:
        predefined_entries += get_feed_entries(url)

    # Ordenar las entradas por fecha de publicación (de más reciente a más antigua)
    predefined_entries.sort(key=get_entry_published, reverse=True)

    # Mezclar las entradas
    random.shuffle(predefined_entries)


    return render_template('index.html', entries=entries, feed_url=feed_url, predefined_entries=predefined_entries)

def get_feed_entries(feed_url):
    feed = feedparser.parse(feed_url)
    entries = []
    for entry in feed.entries:
        entry_data = {
            'title': entry.title,
            'link': entry.link,
            'description': entry.description,
            'source': feed.feed.get('title', 'Unknown Source'),
            'image': None,
        }
        if 'media_thumbnail' in entry:
            entry_data['image'] = entry.media_thumbnail[0]['url']
        elif 'media_content' in entry:
            entry_data['image'] = entry.media_content[0]['url']
        elif 'media_content' in entry:
            entry_data['image'] = entry.enclosure[0]['url']
        else:
            entry_data['image'] = 'static\img\demo.png'
        entries.append(entry_data)
    return entries

if __name__ == '__main__':
    app.run(debug=True)
