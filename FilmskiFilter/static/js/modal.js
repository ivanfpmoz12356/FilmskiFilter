document.addEventListener("DOMContentLoaded", function () {
    const deleteMovieLink = document.getElementById("deleteMovieLink");
    const overlay = document.getElementById("overlay");

    let deleteModal;

    deleteMovieLink.addEventListener("click", function (event) {
        event.preventDefault();

        if (!deleteModal) {
            deleteModal = createDeleteModal();
            document.body.appendChild(deleteModal);
            attachEventListeners(deleteModal);
        }

        deleteModal.style.display = "block";
        overlay.style.display = "block";
        document.body.style.overflow = "hidden";
        overlay.style.pointerEvents = "auto";

        
        disableLinks();
    });

    function createDeleteModal() {
        const modal = document.createElement("div");
        modal.innerHTML = `
            <div class="modal-sadrzaj">
                <p>Jeste li sigurni da želite izbrisati film?</p>
                <div class="modal-prozor">
                    <button id="cancelBtn" class="modal-gumb">Otkaži</button>
                    <button id="deleteBtn" class="modal-gumb">Izbriši</button>
                </div>
            </div>
        `;
        modal.id = "deleteModal";
        return modal;
    }

    function attachEventListeners(deleteModal) {
        const cancelBtn = deleteModal.querySelector("#cancelBtn");
        const deleteBtn = deleteModal.querySelector("#deleteBtn");

        cancelBtn.addEventListener("click", function () {
            closeDeleteModal(deleteModal);
        });

        overlay.addEventListener("click", function (event) {
            if (event.target === overlay) {
                closeDeleteModal(deleteModal);
            }
        });

        deleteBtn.addEventListener("click", function (event) {
            event.stopPropagation(); 
            console.log("Delete button clicked");
        
            
            const movieId = deleteMovieLink.dataset.id; 
            deleteMovie(movieId, deleteModal);
        });
    }

    function closeDeleteModal(deleteModal) {
        deleteModal.style.display = "none";
        overlay.style.display = "none";
        document.body.style.overflow = "auto";
        overlay.style.pointerEvents = "none";

        
        enableLinks();
    }

    function disableLinks() {
       
        const links = document.querySelectorAll("a");
        links.forEach(link => {
            link.addEventListener("click", preventDefault);
            link.style.pointerEvents = "none";
        });
    }

    function enableLinks() {
        
        const links = document.querySelectorAll("a");
        links.forEach(link => {
            link.removeEventListener("click", preventDefault);
            link.style.pointerEvents = "auto";
        });
    }

    function preventDefault(event) {
        event.preventDefault();
    }

    function deleteMovie(movieId, deleteModal) {
        console.log('Deleting movie with ID:', movieId);
    
        fetch(`/delete/${movieId}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            
            console.log('Movie deleted successfully', data);
    
            
            closeDeleteModal(deleteModal);
    
            
            console.log('Redirecting to:', data.redirect);
            window.location.href = data.redirect;
        })
        .catch(error => {
            
            console.error('Error deleting movie:', error);
    
            
            closeDeleteModal(deleteModal);
        });
    }
});
