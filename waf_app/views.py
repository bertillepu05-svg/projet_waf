import json
import os
from datetime import datetime
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# ------------------------------------------------------------
# BASE DE DONNEES DES ARTISTES
# ------------------------------------------------------------
ARTISTS = [
    {
        "name": "Fally Ipupa",
        "album": "Formule 7",
        "year": 2024,
        "origin": "Kinshasa 🇨🇩",
        "genre": "Rumba / R&B",
        "quote": "La musique, c'est l'école de la vie. Chaque note est une leçon, chaque silence une réflexion.",
        "streams": "12M",
        "awards": 18,
        "albums": 9,
        "icon": "microphone",
        "class": "fally",
        "keywords": ["fally", "ipupa", "formule", "rumba", "dictateur"]
    },
    {
        "name": "Innoss'B",
        "album": "Jeune Leader",
        "year": 2025,
        "origin": "Goma 🇨🇩",
        "genre": "Afrobeat / Rumba",
        "quote": "Yo pe na mbangu té, mais j'avance. La jeunesse congolaise a quelque chose à dire au monde.",
        "streams": "45M",
        "awards": 12,
        "albums": 3,
        "icon": "guitar",
        "class": "innoss",
        "keywords": ["innoss", "innoss'b", "jeune", "leader", "afrobeat", "goma"]
    },
    {
        "name": "Gaz Mawete",
        "album": "500",
        "year": 2022,
        "origin": "Kinshasa 🇨🇩",
        "genre": "Rap / Trap",
        "quote": "500 volts dans le microphone. Chaque barz est une décharge électrique pour réveiller les consciences.",
        "streams": "8M",
        "awards": 5,
        "albums": 2,
        "icon": "music",
        "class": "gaz",
        "keywords": ["gaz", "mawete", "500", "rap", "trap"]
    },
    {
        "name": "Fabri GAZ",
        "album": "Dynastie 2",
        "year": 2026,
        "origin": "Kinshasa 🇨🇩",
        "genre": "Rumba / Soukous",
        "quote": "Le Padre de la rumba. La patience est une vertu qui transforme les rêves en réalité.",
        "streams": "20M",
        "awards": 15,
        "albums": 7,
        "icon": "drum",
        "class": "ferre",
        "keywords": ["ferre", "gola", "dynastie", "rumba", "padre", "soukous"]
    },
    {
        "name": "Innoss'B",
        "album": "Jeune Leader",
        "year": 2023,
        "origin": "Goma 🇨🇩",
        "genre": "Afrobeat / Rumba",
        "quote": "Yo pe na mbangu té, mais j'avance. La jeunesse congolaise a quelque chose à dire au monde.",
        "streams": "4M",
        "awards": 8,
        "albums": 3,
        "icon": "microphone",
        "class": "innoss",
        "keywords": ["innoss", "innoss'b", "jeune", "leader", "afrobeat", "goma"]
    },
    {
        "name": "Gaz Mawete",
        "album": "200",
        "year": 2026,
        "origin": "Kinshasa 🇨🇩",
        "genre": "Rap / Trap",
        "quote": "200 volts dans le microphone. Chaque barz est une décharge électrique pour réveiller les consciences.",
        "streams": "5M",
        "awards": 3,
        "albums": 7,
        "icon": "drum",
        "class": "gaz",
        "keywords": ["gaz", "mawete", "200", "rap", "trap"]
    },
]


# ------------------------------------------------------------
# FONCTIONS UTILITAIRES
# ------------------------------------------------------------
def write_log(entry):
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'waf_logs.json'), "a") as f:
        f.write(json.dumps(entry) + "\n")


def check_attack(text, request):
    patterns = {
        "SQL Injection": ["'", '"', " OR ", "1=1", "DROP ", "UNION ", "SELECT ", "--"],
        "XSS": ["<script>", "<script ", "javascript:", "onerror=", "alert(", "onload="],
        "Path Traversal": ["../", "..\\", "/etc/passwd", "boot.ini"],
    }
    for attack_type, keywords in patterns.items():
        for keyword in keywords:
            if keyword.upper() in text.upper():
                return True, attack_type, keyword
    return False, None, None


def search_artists(query):
    """Recherche les artistes par mot-clé (insensible à la casse)"""
    if not query:
        return ARTISTS, False
    
    query_lower = query.lower().strip()
    results = []
    for artist in ARTISTS:
        for keyword in artist["keywords"]:
            if query_lower in keyword.lower():
                results.append(artist)
                break
    
    return results, True


# ------------------------------------------------------------
# PAGE D'ACCUEIL : Le blog protégé
# ------------------------------------------------------------
def blog(request):
    artists, is_search = search_artists("")
    return render(request, 'waf_app/blog.html', {
        'artists': artists,
        'is_search': False
    })


# ------------------------------------------------------------
# RECHERCHE SUR LE BLOG (protégée par WAF)
# ------------------------------------------------------------
def blog_search(request):
    query = request.GET.get('q', '')

    # Vérification WAF d'abord
    is_attack, attack_type, keyword = check_attack(query, request)
    if is_attack:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": request.META.get('REMOTE_ADDR'),
            "attack_type": attack_type,
            "payload": keyword,
            "blocked": True,
            "source_page": "blog_search",
            "full_query": query
        }
        write_log(log_entry)
        return render(request, 'waf_app/blog.html', {
            'artists': ARTISTS,
            'is_search': False,
            'error': f'⛔ <strong>{attack_type}</strong> bloquée par le WAF !<br>Payload : <code>{keyword}</code>'
        })

    # Recherche normale
    artists, is_search = search_artists(query)
    return render(request, 'waf_app/blog.html', {
        'artists': artists,
        'is_search': is_search,
        'query': query,
        'message': f'<i class="fa-solid fa-check"></i> {len(artists)} artiste(s) trouvé(s) pour "<strong>{query}</strong>"' if query else ''
    })


# ------------------------------------------------------------
# COMMENTAIRE SUR LE BLOG (protégé par WAF)
# ------------------------------------------------------------
@csrf_exempt
def blog_comment(request):
    comment = request.POST.get('comment', '')
    is_attack, attack_type, keyword = check_attack(comment, request)
    
    if is_attack:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": request.META.get('REMOTE_ADDR'),
            "attack_type": attack_type,
            "payload": keyword,
            "blocked": True,
            "source_page": "blog_comment",
            "full_query": comment
        }
        write_log(log_entry)
        return render(request, 'waf_app/blog.html', {
            'artists': ARTISTS,
            'is_search': False,
            'error': f'⛔ Commentaire bloqué ! <strong>{attack_type}</strong> détectée.'
        })

    return render(request, 'waf_app/blog.html', {
        'artists': ARTISTS,
        'is_search': False,
        'message': '<i class="fa-solid fa-check"></i> ✅ Votre commentaire a été publié avec succès !'
    })


# ------------------------------------------------------------
# PAGE TEST WAF
# ------------------------------------------------------------
def test_waf(request):
    return render(request, 'waf_app/test_waf.html')


# ------------------------------------------------------------
# ENDPOINT DE TEST WAF
# ------------------------------------------------------------
def waf_check(request):
    query = request.GET.get('q', '')
    if not query:
        return render(request, 'waf_app/test_waf.html')

    is_attack, attack_type, keyword = check_attack(query, request)

    if is_attack:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": request.META.get('REMOTE_ADDR'),
            "attack_type": attack_type,
            "payload": keyword,
            "blocked": True,
            "source_page": "test_waf",
            "full_query": query
        }
        write_log(log_entry)
        return render(request, 'waf_app/test_waf.html', {
            'result': True, 'blocked': True, 'query': query
        })

    return render(request, 'waf_app/test_waf.html', {
        'result': True, 'blocked': False, 'query': query
    })


# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------
def dashboard(request):
    log_file = os.path.join(settings.BASE_DIR, 'logs', 'waf_logs.json')
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            for line in f:
                try:
                    logs.append(json.loads(line.strip()))
                except:
                    pass

    logs.reverse()
    sql_count = sum(1 for log in logs if log.get('attack_type') == 'SQL Injection')
    xss_count = sum(1 for log in logs if log.get('attack_type') == 'XSS')
    path_count = sum(1 for log in logs if log.get('attack_type') == 'Path Traversal')

    return render(request, 'waf_app/dashboard.html', {
        'logs': logs[:50], 'total_attacks': len(logs),
        'sql_count': sql_count, 'xss_count': xss_count, 'path_count': path_count,
    })