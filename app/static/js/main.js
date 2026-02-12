async function handleSubmit(e) {
    e.preventDefault();

    const urlInput = document.getElementById('urlInput');
    const customCode = document.getElementById('customCode').value.trim();
    const btn = document.getElementById('submitBtn');
    const resultContainer = document.getElementById('resultContainer');
    const errorContainer = document.getElementById('errorContainer');

    resultContainer.classList.remove('visible');
    errorContainer.classList.remove('visible');

    btn.classList.add('loading');

    const body = { url: urlInput.value.trim() };
    if (customCode) {
        body.custom_code = customCode;
    }

    try {
        const response = await fetch('/api/shorten', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        const data = await response.json();

        if (response.ok) {
            showResult(data);
        } else {
            showError(data.detail || 'Произошла ошибка');
        }
    } catch (err) {
        showError('Сервер недоступен. Попробуйте позже.');
    } finally {
        btn.classList.remove('loading');
    }
}

function showResult(data) {
    const container = document.getElementById('resultContainer');
    const shortUrlEl = document.getElementById('shortUrl');
    const originalUrlEl = document.getElementById('originalUrl');

    shortUrlEl.href = data.short_url;
    shortUrlEl.textContent = data.short_url;
    originalUrlEl.textContent = '→ ' + data.original_url;

    requestAnimationFrame(() => {
        container.classList.add('visible');
    });

    if (window.innerWidth <= 768) {
        setTimeout(() => {
            container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 300);
    }
}

function showError(message) {
    const container = document.getElementById('errorContainer');
    const errorCard = document.getElementById('errorCard');
    const errorText = document.getElementById('errorText');

    errorText.textContent = message;

    errorCard.style.animation = 'none';
    errorCard.offsetHeight;
    errorCard.style.animation = '';

    requestAnimationFrame(() => {
        container.classList.add('visible');
    });
}

async function copyToClipboard() {
    const url = document.getElementById('shortUrl').textContent;
    const btn = document.getElementById('copyBtn');
    const icon = document.getElementById('copyIcon');

    try {
        await navigator.clipboard.writeText(url);

        btn.classList.add('copied');
        icon.textContent = '✅';

        setTimeout(() => {
            btn.classList.remove('copied');
            icon.textContent = '📋';
        }, 2000);
    } catch (err) {
        const textarea = document.createElement('textarea');
        textarea.value = url;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);

        btn.classList.add('copied');
        icon.textContent = '✅';
        setTimeout(() => {
            btn.classList.remove('copied');
            icon.textContent = '📋';
        }, 2000);
    }
}

function initRippleEffect() {
    const btn = document.getElementById('submitBtn');
    
    btn.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;

        this.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initRippleEffect();
});
