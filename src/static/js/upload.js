document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' || event.key === 'F5') {
            event.preventDefault();

            sessionStorage.removeItem('pageWasVisited');
            window.location.href = '/';
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const fileUpload = document.getElementById('file-upload');
    const imagesButton = document.getElementById('images-tab-btn');
    const dropzone = document.querySelector('.upload__dropzone');
    const currentUploadInput = document.querySelector('.upload__input');
    const copyButton = document.querySelector('.upload__copy');

    const updateTabStyles = () => {
        const uploadTab = document.getElementById('upload-tab-btn');
        const imagesTab = document.getElementById('images-tab-btn');
        const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];

        const isImagesPage = window.location.pathname.includes('images.html');

        uploadTab.classList.remove('upload__tab--active');
        imagesTab.classList.remove('upload__tab--active');

        if (isImagesPage) {
            imagesTab.classList.add('upload__tab--active');
        } else {
            uploadTab.classList.add('upload__tab--active');
        }
    };

    // validator
    const handleAndStoreFiles = (files) => {
        const promptElement = document.querySelector('.upload__promt');
        const originalText = promptElement.innerText;

        if (!files || files.length === 0) return;

        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const MAX_SIZE_MB = 5;
        const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

        let addedCount = 0;
        let errorMsg = "";

        const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];

        for (const file of files) {
            if (!allowedTypes.includes(file.type)) {
                errorMsg = "Error: Only image!";
                continue;
            }

            if (file.size > MAX_SIZE_BYTES) {
                errorMsg = "Error: File more 5Mb!";
                continue;
            }

            const reader = new FileReader();
            reader.onload = (event) => {
                storedFiles.push({ name: file.name, url: event.target.result });
                localStorage.setItem('uploadedImages', JSON.stringify(storedFiles));
                if (typeof updateTabStyles === 'function') updateTabStyles();
            };
            reader.readAsDataURL(file);

            addedCount++;
        }

        if (addedCount > 0 && !errorMsg) {
            promptElement.innerText = `✅ Successfully downloaded: ${addedCount}`;
            promptElement.style.color = "#2ecc71";
        } else if (addedCount > 0 && errorMsg) {
            promptElement.innerText = `⚠️ Added ${addedCount}, part with error`;
            promptElement.style.color = "#f39c12";
        } else if (errorMsg) {
            promptElement.innerText = `❌ ${errorMsg}`;
            promptElement.style.color = "#e74c3c";
        }

        setTimeout(() => {
            promptElement.innerText = originalText;
            promptElement.style.color = "";
        }, 3000);
    };


    if (copyButton && currentUploadInput) {
        copyButton.addEventListener('click', () => {
            const textToCopy = currentUploadInput.value;

            if (textToCopy && textToCopy !== 'https://') {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    copyButton.textContent = 'COPIED!';
                    setTimeout(() => {
                        copyButton.textContent = 'COPY';
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            }
        });
    }

    if (imagesButton) {
        imagesButton.addEventListener('click', () => {
            window.location.href = '/images-list';
        });
    }

    fileUpload.addEventListener('change', (event) => {
        handleAndStoreFiles(event.target.files);
        event.target.value = '';
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    dropzone.addEventListener('drop', (event) => {
        handleAndStoreFiles(event.dataTransfer.files);
    });

    updateTabStyles();
});