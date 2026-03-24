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

    const ITEMS_PER_PAGE = 10;
    let currentPage = 1;
    let totalImages = 0;

    const renderPagination = () => {
        const existingPagination = document.getElementById('pagination-wrapper');
        if (existingPagination) existingPagination.remove();

        const totalPages = Math.ceil(totalImages / ITEMS_PER_PAGE);
        if (totalPages <= 1) return;

        const pagination = document.createElement('div');
        pagination.id = 'pagination-wrapper';
        pagination.className = 'pagination-wrapper';

        const prevBtn = document.createElement('button');
        prevBtn.className = 'pagination-btn pagination-prev';
        prevBtn.innerHTML = '&larr;';
        prevBtn.disabled = currentPage === 1;
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                displayFiles();
            }
        });

        const nextBtn = document.createElement('button');
        nextBtn.className = 'pagination-btn pagination-next';
        nextBtn.innerHTML = '&rarr;';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                displayFiles();
            }
        });

        const pageNumbers = document.createElement('div');
        pageNumbers.className = 'pagination-pages';

        const createPageBtn = (page) => {
            const btn = document.createElement('button');
            btn.className = 'pagination-btn pagination-page' + (page === currentPage ? ' active' : '');
            btn.textContent = page;
            btn.addEventListener('click', () => {
                if (page !== currentPage) {
                    currentPage = page;
                    displayFiles();
                }
            });
            return btn;
        };

        const addEllipsis = () => {
            const span = document.createElement('span');
            span.className = 'pagination-ellipsis';
            span.textContent = '…';
            pageNumbers.appendChild(span);
        };

        if (totalPages <= 7) {
            for (let i = 1; i <= totalPages; i++) {
                pageNumbers.appendChild(createPageBtn(i));
            }
        } else {
            pageNumbers.appendChild(createPageBtn(1));
            if (currentPage > 3) addEllipsis();
            const start = Math.max(2, currentPage - 1);
            const end = Math.min(totalPages - 1, currentPage + 1);
            for (let i = start; i <= end; i++) {
                pageNumbers.appendChild(createPageBtn(i));
            }
            if (currentPage < totalPages - 2) addEllipsis();
            pageNumbers.appendChild(createPageBtn(totalPages));
        }

        pagination.appendChild(prevBtn);
        pagination.appendChild(pageNumbers);
        pagination.appendChild(nextBtn);

        fileListWrapper.after(pagination);
    };

    const displayFiles = async () => {
        fileListWrapper.innerHTML = '';

        try {
            const response = await fetch(`/api/images?page=${currentPage}`);
            const result = await response.json();

            if (!result.success || result.images.length === 0) {
                fileListWrapper.innerHTML = '<p class="upload__promt" style="text-align: center; margin-top: 50px;">No images uploaded yet.</p>';
                totalImages = 0;
                renderPagination();
                return;
            }

            totalImages = result.total;

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
            renderPagination();
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
                        // If we deleted the last item on a page > 1, go back one page
                        const totalPages = Math.ceil((totalImages - 1) / ITEMS_PER_PAGE);
                        if (currentPage > totalPages && currentPage > 1) {
                            currentPage--;
                        }
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
