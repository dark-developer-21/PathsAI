function openAgent() {
    const btn = event.target.closest('.search-btn');
    btn.style.transform = 'scale(0.98)';
    
    setTimeout(() => {
        window.location.href = 'voice-assistant.html';
    }, 150);
}

function selectOption(option) {
    const btn = event.target.closest('.nav-btn');
    btn.style.transform = 'scale(0.96)';
    
    setTimeout(() => {
        if (option === 'favorites') {
            console.log('Mis Lugares seleccionado');
            // Navigate to favorites view
        } else if (option === 'places') {
            console.log('Explorar lugares seleccionado');
            // Navigate to explore places view
        }
    }, 150);
}
