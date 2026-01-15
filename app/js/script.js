function selectProduct(productId) {
    const card = document.getElementById(productId);
    card.style.transform = 'scale(0.98)';
    
    setTimeout(() => {
        card.style.transform = '';
        
        // Store selection in localStorage
        localStorage.setItem('selectedProduct', productId);
        
        // Both options redirect to navigation page
        window.location.href = 'navigation.html';
    }, 150);
}
