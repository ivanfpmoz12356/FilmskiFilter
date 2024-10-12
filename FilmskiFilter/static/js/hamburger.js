    function myFunction() {
        var dropdownContent = document.querySelector(".dropdown__content");
        dropdownContent.classList.toggle("show");
    }
    
    // Close the dropdown if the user clicks outside of it
    window.addEventListener("click", function(event) {
        var dropdownContent = document.querySelector(".dropdown__content");
        var icon = document.querySelector(".nav .icon");
        
        if (!event.target.matches('.icon') && !event.target.matches('.dropdown__content')) {
            dropdownContent.classList.remove('show');
        }
    });

    // Close the menu when the screen width goes above 600px
    window.addEventListener("resize", function() {
        var x = document.getElementById("myTopnav");
        if (window.innerWidth > 600) {
            x.className = "nav";
        }
    });
