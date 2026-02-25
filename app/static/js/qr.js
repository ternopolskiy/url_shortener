/**
 * QR Codes Module - Frontend Logic
 * Gosha Connections Platform
 */

// State
let currentPage = 1;
let currentPerPage = 12;
let currentQRCode = null;
let logoBase64 = null;
let previewTimeout = null;

// Current settings
let currentSettings = {
    style: 'square',
    foregroundColor: '#000000',
    backgroundColor: '#FFFFFF',
    boxSize: 10,
    borderSize: 4,
    errorCorrection: 'M'
};

// ============================================
// Load QR Codes
// ============================================
async function loadQRCodes() {
    const grid = document.getElementById('qrCodesGrid');
    const search = document.getElementById('searchInput').value;
    const perPageSelect = document.getElementById('perPageSelect');
    
    currentPage = 1;
    currentPerPage = parseInt(perPageSelect.value) || 12;
    
    try {
        const response = await API.request(
            `/api/v1/qr?page=${currentPage}&per_page=${currentPerPage}&search=${encodeURIComponent(search)}`
        );
        
        const data = await response.json();
        
        if (data.items.length === 0) {
            grid.innerHTML = `
                <div style="text-align: center; padding: 60px; color: var(--text-muted); grid-column: 1/-1;">
                    <div style="font-size: 48px; margin-bottom: 16px;">📱</div>
                    <p>No QR codes yet. Create your first QR code!</p>
                </div>
            `;
            document.getElementById('pagination').style.display = 'none';
            return;
        }
        
        renderQRCodes(data.items);
        renderPagination(data);
        
    } catch (error) {
        grid.innerHTML = `
            <div style="text-align: center; padding: 60px; color: var(--error); grid-column: 1/-1;">
                <div style="font-size: 48px; margin-bottom: 16px;">❌</div>
                <p>Failed to load QR codes</p>
            </div>
        `;
    }
}

async function loadQRCodesPage(page) {
    const grid = document.getElementById('qrCodesGrid');
    const search = document.getElementById('searchInput').value;
    
    currentPage = page;
    
    try {
        const response = await API.request(
            `/api/v1/qr?page=${page}&per_page=${currentPerPage}&search=${encodeURIComponent(search)}`
        );
        
        const data = await response.json();
        renderQRCodes(data.items);
        renderPagination(data);
        
        // Scroll to top of grid
        grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (error) {
        Toast.show('Failed to load QR codes', 'error');
    }
}

function renderQRCodes(items) {
    const grid = document.getElementById('qrCodesGrid');
    
    grid.innerHTML = items.map(qr => `
        <div class="qr-card" onclick="viewQRCode(${qr.id})">
            <div class="qr-card__image">
                <img src="data:image/png;base64,${qr.qr_image_base64}" alt="QR Code">
            </div>
            <div class="qr-card__title">${escapeHtml(qr.title || 'Untitled QR Code')}</div>
            <div class="qr-card__content">${escapeHtml(qr.content)}</div>
            <div class="qr-card__meta">
                <span>📥 ${qr.downloads_count} downloads</span>
                <span>${formatDate(qr.created_at)}</span>
            </div>
            <div class="qr-card__actions">
                <button class="btn btn--secondary" style="flex: 1; padding: 8px;" onclick="event.stopPropagation(); downloadQRFromCard(${qr.id})">
                    ⬇️ Download
                </button>
                <button class="btn btn--ghost" style="padding: 8px; color: var(--error);" onclick="event.stopPropagation(); deleteQRCode(${qr.id})">
                    🗑️
                </button>
            </div>
        </div>
    `).join('');
}

function renderPagination(data) {
    const pagination = document.getElementById('pagination');
    
    if (data.pages <= 1) {
        pagination.style.display = 'none';
        return;
    }
    
    pagination.style.display = 'flex';
    
    let html = '';
    
    // Previous button
    html += `<button ${data.page === 1 ? 'disabled' : ''} onclick="loadQRCodesPage(${data.page - 1})">← Prev</button>`;
    
    // Page numbers
    for (let i = 1; i <= data.pages; i++) {
        if (i === 1 || i === data.pages || (i >= data.page - 2 && i <= data.page + 2)) {
            html += `<button class="${i === data.page ? 'active' : ''}" onclick="loadQRCodesPage(${i})">${i}</button>`;
        } else if (i === data.page - 3 || i === data.page + 3) {
            html += `<button disabled>...</button>`;
        }
    }
    
    // Next button
    html += `<button ${data.page === data.pages ? 'disabled' : ''} onclick="loadQRCodesPage(${data.page + 1})">Next →</button>`;
    
    pagination.innerHTML = html;
}

// ============================================
// Modal Functions
// ============================================
function openCreateModal() {
    document.getElementById('createModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
    resetForm();
}

function closeCreateModal() {
    document.getElementById('createModal').style.display = 'none';
    document.body.style.overflow = '';
}

function viewQRCode(id) {
    currentQRCode = id;
    
    API.request(`/api/v1/qr/${id}`)
        .then(response => response.json())
        .then(qr => {
            document.getElementById('viewTitle').textContent = qr.title || 'QR Code';
            document.getElementById('viewContent').textContent = qr.content;
            document.getElementById('viewQRImage').src = `data:image/png;base64,${qr.qr_image_base64}`;
            document.getElementById('viewDownloads').textContent = qr.downloads_count;
            document.getElementById('viewCreated').textContent = formatDate(qr.created_at);
            document.getElementById('viewModal').style.display = 'flex';
            document.body.style.overflow = 'hidden';
        })
        .catch(() => Toast.show('Failed to load QR code', 'error'));
}

function closeViewModal() {
    document.getElementById('viewModal').style.display = 'none';
    document.body.style.overflow = '';
}

// ============================================
// Form Functions
// ============================================
function resetForm() {
    const qrContent = document.getElementById('qrContent');
    const qrTitle = document.getElementById('qrTitle');
    const fgColorPicker = document.getElementById('fgColorPicker');
    const fgColorText = document.getElementById('fgColorText');
    const bgColorPicker = document.getElementById('bgColorPicker');
    const bgColorText = document.getElementById('bgColorText');
    const boxSizeSlider = document.getElementById('boxSizeSlider');
    const borderSizeSlider = document.getElementById('borderSizeSlider');
    const boxSizeValue = document.getElementById('boxSizeValue');
    const borderSizeValue = document.getElementById('borderSizeValue');
    const errorCorrection = document.getElementById('errorCorrection');
    const previewContainer = document.getElementById('previewContainer');
    const previewLoading = document.getElementById('previewLoading');
    const logoUpload = document.getElementById('logoUpload');
    const logoPreview = document.getElementById('logoPreview');
    
    if (qrContent) qrContent.value = '';
    if (qrTitle) qrTitle.value = '';
    if (fgColorPicker) fgColorPicker.value = '#000000';
    if (fgColorText) fgColorText.value = '#000000';
    if (bgColorPicker) bgColorPicker.value = '#FFFFFF';
    if (bgColorText) bgColorText.value = '#FFFFFF';
    if (boxSizeSlider) boxSizeSlider.value = 10;
    if (borderSizeSlider) borderSizeSlider.value = 4;
    if (boxSizeValue) boxSizeValue.textContent = '10';
    if (borderSizeValue) borderSizeValue.textContent = '4';
    if (errorCorrection) errorCorrection.value = 'M';
    
    if (previewContainer) {
        previewContainer.innerHTML = `
            <div id="qrPreview" style="width: 256px; height: 256px; display: flex; align-items: center; justify-content: center; background: var(--bg-secondary); border-radius: var(--radius-lg); border: 2px dashed var(--border-default);">
                <p style="color: var(--text-muted);">Enter URL to preview</p>
            </div>
        `;
    }
    if (previewLoading) previewLoading.style.display = 'none';

    // Reset style selection
    document.querySelectorAll('.style-option').forEach(opt => opt.classList.remove('selected'));
    const squareOption = document.querySelector('.style-option[data-style="square"]');
    if (squareOption) squareOption.classList.add('selected');

    // Reset logo
    logoBase64 = null;
    if (logoUpload) logoUpload.value = '';
    if (logoPreview) logoPreview.style.display = 'none';

    // Reset settings
    currentSettings = {
        style: 'square',
        foregroundColor: '#000000',
        backgroundColor: '#FFFFFF',
        boxSize: 10,
        borderSize: 4,
        errorCorrection: 'M'
    };
}

function selectStyle(style) {
    currentSettings.style = style;
    
    document.querySelectorAll('.style-option').forEach(opt => {
        opt.classList.toggle('selected', opt.dataset.style === style);
    });
    
    debouncePreview();
}

function updateColor(type, value) {
    if (type === 'foreground') {
        currentSettings.foregroundColor = value;
        document.getElementById('fgColorPicker').value = value;
        document.getElementById('fgColorText').value = value;
    } else {
        currentSettings.backgroundColor = value;
        document.getElementById('bgColorPicker').value = value;
        document.getElementById('bgColorText').value = value;
    }
    
    debouncePreview();
}

function updateSlider(type, value) {
    if (type === 'boxSize') {
        currentSettings.boxSize = parseInt(value);
        document.getElementById('boxSizeValue').textContent = value;
    } else {
        currentSettings.borderSize = parseInt(value);
        document.getElementById('borderSizeValue').textContent = value;
    }
    
    debouncePreview();
}

function handleLogoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Check file size (max 500KB)
    if (file.size > 500 * 1024) {
        Toast.show('File too large. Max 500KB', 'error');
        event.target.value = '';
        return;
    }
    
    // Check file type
    const validTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        Toast.show('Invalid file type. Use PNG, JPG, GIF, or WebP', 'error');
        event.target.value = '';
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        logoBase64 = e.target.result;
        
        // Show preview
        document.getElementById('logoPreviewImg').src = logoBase64;
        document.getElementById('logoPreview').style.display = 'block';
        
        debouncePreview();
    };
    reader.readAsDataURL(file);
}

function removeLogo() {
    logoBase64 = null;
    document.getElementById('logoUpload').value = '';
    document.getElementById('logoPreview').style.display = 'none';
    debouncePreview();
}

function debouncePreview() {
    if (previewTimeout) clearTimeout(previewTimeout);
    previewTimeout = setTimeout(generatePreview, 500);
}

async function generatePreview() {
    const contentEl = document.getElementById('qrContent');
    const previewContainer = document.getElementById('qrPreview');
    const loadingIndicator = document.getElementById('previewLoading');
    
    if (!previewContainer) return;
    
    const content = contentEl ? contentEl.value.trim() : '';

    if (!content) {
        previewContainer.innerHTML = `
            <div style="width: 256px; height: 256px; display: flex; align-items: center; justify-content: center; background: var(--bg-secondary); border-radius: var(--radius-lg); border: 2px dashed var(--border-default);">
                <p style="color: var(--text-muted);">Enter URL to preview</p>
            </div>
        `;
        return;
    }

    // Show loading
    if (loadingIndicator) loadingIndicator.style.display = 'block';

    try {
        const response = await API.request('/api/v1/qr/preview', {
            method: 'POST',
            body: JSON.stringify({
                content: content,
                foreground_color: currentSettings.foregroundColor,
                background_color: currentSettings.backgroundColor,
                style: currentSettings.style,
                box_size: currentSettings.boxSize,
                border_size: currentSettings.borderSize,
                error_correction: currentSettings.errorCorrection,
                logo_base64: logoBase64
            })
        });

        const data = await response.json();

        previewContainer.innerHTML = `
            <img src="data:image/png;base64,${data.qr_image_base64}"
                 alt="QR Preview"
                 style="width: 256px; height: 256px; object-fit: contain;">
        `;

    } catch (error) {
        previewContainer.innerHTML = `
            <div style="width: 256px; height: 256px; display: flex; align-items: center; justify-content: center; background: var(--error-light); border-radius: var(--radius-lg); border: 2px dashed var(--error);">
                <p style="color: var(--error);">Preview failed</p>
            </div>
        `;
    } finally {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
    }
}

// ============================================
// Create QR Code
// ============================================
async function createQRCode() {
    const content = document.getElementById('qrContent').value.trim();
    const title = document.getElementById('qrTitle').value.trim();
    
    if (!content) {
        Toast.show('Please enter a URL or content', 'error');
        return;
    }
    
    try {
        const response = await API.request('/api/v1/qr', {
            method: 'POST',
            body: JSON.stringify({
                content: content,
                title: title || undefined,
                foreground_color: currentSettings.foregroundColor,
                background_color: currentSettings.backgroundColor,
                style: currentSettings.style,
                box_size: currentSettings.boxSize,
                border_size: currentSettings.borderSize,
                error_correction: currentSettings.errorCorrection,
                logo_base64: logoBase64
            })
        });
        
        if (response.ok) {
            Toast.show('QR code created successfully!', 'success');
            closeCreateModal();
            loadQRCodes();
        }
        
    } catch (error) {
        Toast.show(error.message || 'Failed to create QR code', 'error');
    }
}

// ============================================
// Download QR Code
// ============================================
async function downloadQR(format) {
    if (!currentQRCode) return;
    
    try {
        const response = await API.request(`/api/v1/qr/${currentQRCode}/download/${format}`);
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `qr_${currentQRCode}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        Toast.show(`QR code downloaded as ${format.toUpperCase()}`, 'success');
        closeViewModal();
        
        // Update downloads count in view
        const qrData = await API.request(`/api/v1/qr/${currentQRCode}`);
        const qr = await qrData.json();
        document.getElementById('viewDownloads').textContent = qr.downloads_count;
        
    } catch (error) {
        Toast.show('Failed to download QR code', 'error');
    }
}

async function downloadQRFromCard(id) {
    try {
        const response = await API.request(`/api/v1/qr/${id}/download/png`);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `qr_${id}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        Toast.show('QR code downloaded!', 'success');
    } catch (error) {
        Toast.show('Failed to download QR code', 'error');
    }
}

// ============================================
// Delete QR Code
// ============================================
async function deleteQRCode(id) {
    if (!confirm('Are you sure you want to delete this QR code?')) return;
    
    try {
        const response = await API.request(`/api/v1/qr/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok || response.status === 204) {
            Toast.show('QR code deleted', 'success');
            loadQRCodes();
        }
        
    } catch (error) {
        Toast.show('Failed to delete QR code', 'error');
    }
}

// ============================================
// Utility Functions
// ============================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

// ============================================
// Initialize
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    loadQRCodes();
});

// Close modals on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeCreateModal();
        closeViewModal();
    }
});
