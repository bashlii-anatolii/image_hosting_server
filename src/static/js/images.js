document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'F5' || event.key === 'Escape') {
            event.preventDefault();
            window.location.href = '/upload';
        }
    });

    const fileListWrapper = document.getElementById('file-list-wrapper');
    const uploadRedirectButton = document.getElementById('upload-tab-btn');

    if (uploadRedirectButton) {
        uploadRedirectButton.addEventListener('click', () => {
            window.location.href = '/upload';
        });
    }

    const displayFiles = async () => {
        fileListWrapper.innerHTML = '';

        let storedFiles = [];
        try {
            const res = await fetch('/images');
            storedFiles = await res.json();
        } catch (err) {
            console.error(err);
        }

        if (storedFiles.length === 0) {
            fileListWrapper.innerHTML = '<p class="upload__promt" style="text-align: center; margin-top: 50px;">No images uploaded yet.</p>';
            return;
        }

        const container = document.createElement('div');
        container.className = 'file-list-container';

        const header = document.createElement('div');
        header.className = 'file-list-header';
        header.innerHTML = `
            <div class="file-col file-col-name">Name</div>
            <div class="file-col file-col-url">Url</div>
            <div class="file-col file-col-delete">Delete</div>
        `;
        container.appendChild(header);

        const list = document.createElement('div');
        list.id = 'file-list';

        storedFiles.forEach((fileData, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-list-item';
            fileItem.innerHTML = `
                <div class="file-col file-col-name">
                    <span class="file-icon">
                        <img src="../static/img/icon/Group.png" alt="file icon">
                        <img src="${fileData.preview}" alt="preview" class="image-preview">
                    </span>
                    <span class="file-name">${fileData.name}</span>
                </div>
                <div class="file-col file-col-url">http://image-hosting-server.com/${fileData.name}</div>
                <div class="file-col file-col-delete">
                    <button class="delete-btn" data-filename="${fileData.name}"><img src="../static/img/icon/delete.png" alt="delete icon"></button>
                </div>
            `;
            list.appendChild(fileItem);
        });

        container.appendChild(list);
        fileListWrapper.appendChild(container);
        addDeleteListeners();
        updateTabStyles();
    };

    const addDeleteListeners = () => {
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const filename = event.currentTarget.dataset.filename;

                try {
                    const response = await fetch('/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filename })
                    });
                    const result = await response.json();
                    if (!result.success) console.error(result.message);
                } catch (error) {
                    console.error(error);
                }

                displayFiles();
            });
        });
    };

    displayFiles();
});