let envelopeOpen = false;
let currentLightboxIndex = 0;
let flameVisible = true;

// Loading Screen - se oculta siempre
window.addEventListener('load', function() {
    setTimeout(function() {
        var loading = document.getElementById('loading');
        if (loading) {
            loading.classList.add('hidden');
        }
    }, 100);
});

// Fallback por si load no dispara
setTimeout(function() {
    var loading = document.getElementById('loading');
    if (loading) {
        loading.classList.add('hidden');
    }
}, 3000);

// Envelope
function openEnvelope() {
    const wrapper = document.querySelector('.envelope-wrapper');
    if (!wrapper) return;
    
    if (!envelopeOpen) {
        wrapper.classList.add('open');
        launchConfetti(80);
    } else {
        wrapper.classList.remove('open');
    }
    envelopeOpen = !envelopeOpen;
}

// Confetti
function launchConfetti(count) {
    const defaults = {
        spread: 360,
        ticks: 150,
        colors: ['#a855f7', '#06b6d4', '#fbbf24', '#10b981', '#fff']
    };
    confetti({
        particleCount: count || 50,
        startVelocity: 45,
        ...defaults
    });
}

// Candles
function blowCandles() {
    if (!flameVisible) return;
    flameVisible = false;
    
    const flame = document.querySelector('.flame');
    if (flame) {
        flame.style.opacity = '0';
    }
    
    launchConfetti(150);
    
    const btn = document.querySelector('.cake-section .btn-cta');
    if (btn) {
        btn.textContent = '🎉 ¡Deseo pedido! ✨';
    }
}

// Celebration
function startCelebration() {
    const duration = 10000;
    const end = Date.now() + duration;
    
    launchConfetti(200);
    
    const interval = setInterval(() => {
        if (Date.now() > end) {
            clearInterval(interval);
            return;
        }
        launchConfetti(50);
    }, 300);
}

// Lazy loading con thumbnails
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                    }
                    observer.unobserve(img);
                }
            });
        }, { rootMargin: '50px' });
        
        lazyImages.forEach(function(img) {
            observer.observe(img);
        });
    } else {
        lazyImages.forEach(function(img) {
            const src = img.getAttribute('data-src');
            if (src) {
                img.src = src;
                img.removeAttribute('data-src');
            }
        });
    }
});
    const lightbox = document.getElementById('lightbox');
    const mainImages = lightbox?.querySelectorAll('.lightbox-main img');
    const thumbs = lightbox?.querySelectorAll('.lightbox-thumb');
    const caption = document.getElementById('lightboxCaption');
    
    if (!lightbox || !mainImages?.length) return;
    
    currentLightboxIndex = index;
    
    mainImages.forEach((img, i) => {
        img.style.display = i === index ? 'block' : 'none';
    });
    
    thumbs?.forEach((thumb, i) => {
        thumb.classList.toggle('active', i === index);
    });
    
    if (caption) {
        caption.textContent = thumbs?.[index]?.querySelector('img')?.alt || '';
    }
    
    document.getElementById('lightboxCurrent').textContent = index + 1;
    
    lightbox.classList.add('show');
}

function closeLightbox() {
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        lightbox.classList.remove('show');
    }
}

function changeLightbox(direction) {
    const lightbox = document.getElementById('lightbox');
    const total = lightbox?.querySelectorAll('.lightbox-thumb').length || 0;
    
    if (total === 0) return;
    
    currentLightboxIndex = (currentLightboxIndex + direction + total) % total;
    openLightbox(currentLightboxIndex);
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    const lightbox = document.getElementById('lightbox');
    if (!lightbox?.classList.contains('show')) return;
    
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') changeLightbox(-1);
    if (e.key === 'ArrowRight') changeLightbox(1);
});

// Close lightbox on backdrop click
document.getElementById('lightbox')?.addEventListener('click', (e) => {
    if (e.target.id === 'lightbox') closeLightbox();
});

// Auto celebration
setTimeout(() => {
    launchConfetti(30);
    setInterval(() => launchConfetti(20), 3000);
}, 3000);