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

    const uploadFile = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];

                const getNextImageNumber = () =>
                    storedFiles.filter(f => f.displayName && f.displayName.startsWith('image')).length + 1;

                const ext = file.name.substring(file.name.lastIndexOf('.'));

                const displayName = `image${String(getNextImageNumber()).padStart(2, '0')}${ext}`;

                storedFiles.push({
                    name: data.filename,
                    displayName: displayName,
                    originalName: file.name,
                    url: `https://image-hosting-server.com/${data.filename}`
                });

                localStorage.setItem('uploadedImages', JSON.stringify(storedFiles));

                if (currentUploadInput) {
                    currentUploadInput.value = `https://image-hosting-server.com/${data.filename}`;
                }

                showMessage('File uploaded successfully!');
            } else {
                showMessage(data.message || 'Upload failed.', true);
            }

        } catch (err) {
            console.error(err);
            showMessage('Something went wrong. Please try again.', true);
        }
    };

    // validator
    const handleAndStoreFiles = async (files) => {
        const promptElement = document.querySelector('.upload__promt');
        const originalText = promptElement.innerText;

        if (!files || files.length === 0) return;

        let addedCount = 0;
        let errorMsg = "";

        for (const file of files) {
            const formData = new FormData();
            formData.append("file", file);

            try {
                const response = await fetch("/upload", {
                    method: "POST",
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    addedCount++;

                    if (currentUploadInput) {
                        currentUploadInput.value = result.url;
                    }

                } else {
                    errorMsg = result.message;
                }

            } catch (e) {
                errorMsg = "Server error";
            }
        }

        if (addedCount > 0 && !errorMsg) {
            promptElement.innerText = `✅ Successfully uploaded: ${addedCount}`;
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
