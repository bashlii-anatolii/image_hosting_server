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

        try {
            const response = await fetch('/api/images');
            const result = await response.json();

            if (!result.success || result.images.length === 0) {
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

            result.images.forEach((image) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-list-item';
                fileItem.innerHTML = `
                    <div class="file-col file-col-name">
                        <span class="file-icon">
                            <img src="../static/img/icon/Group.png" alt="file icon">
                            <img src="/images/${image.filename}" alt="preview" class="image-preview">
                        </span>
                        <span class="file-name">${image.original_name}</span>
                    </div>
                    <div class="file-col file-col-url">https://image-hosting-server.com/${image.filename}</div>
                    <div class="file-col file-col-delete">
                        <button class="delete-btn" data-id="${image.id}"><img src="../static/img/icon/delete.png" alt="delete icon"></button>
                    </div>
                `;
                list.appendChild(fileItem);
            });

            container.appendChild(list);
            fileListWrapper.appendChild(container);
            addDeleteListeners();

        } catch (error) {
            console.error('Error fetching images:', error);
            fileListWrapper.innerHTML = '<p class="upload__promt" style="text-align: center; margin-top: 50px;">Error loading images.</p>';
        }
    };

    const addDeleteListeners = () => {
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const imageId = event.currentTarget.dataset.id;

                try {
                    const response = await fetch(`/api/images/${imageId}`, {
                        method: 'DELETE'
                    });
                    const result = await response.json();

                    if (result.success) {
                        displayFiles();
                    } else {
                        console.error('Failed to delete:', result.message);
                    }
                } catch (error) {
                    console.error('Error deleting:', error);
                }
            });
        });
    };

    displayFiles();
});