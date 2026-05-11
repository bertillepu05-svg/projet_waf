// ===== EXEMPLE DANS LE FORMULAIRE DE TEST =====
function useExample(element) {
    const spans = element.querySelectorAll('span');
    let text = '';
    
    if (spans.length >= 2) {
        // Prendre le deuxième span (après l'icône)
        text = spans[1].textContent.trim();
    } else {
        // Fallback : prendre tout le texte sauf le tag
        text = element.textContent.replace(/\s+/g, ' ').trim();
        // Enlever le texte du tag si présent
        const tag = element.querySelector('.tag');
        if (tag) {
            text = text.replace(tag.textContent, '').trim();
        }
    }

    const input = document.querySelector('input[name="q"]');
    if (input) {
        input.value = text;
        input.focus();
    }
}

// ===== CONFIRMATION AVANT DE QUITTER LE DASHBOARD =====
const dashboardPage = document.querySelector('.stats-grid');
if (dashboardPage) {
    console.log('📊 Dashboard WAF chargé — Les statistiques sont mises à jour en temps réel');
}

// ===== ANIMATION DOUCE AU SCROLL =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

console.log('🛡️ GOMABEATS WAF - Système de protection activé');
console.log('📁 Logs enregistrés dans : /logs/waf_logs.json');
console.log('📊 Dashboard ELK accessible sur : http://localhost:5601');