    let regexPseudo = /^(?=[^A-Z]*(?:[A-Z][^A-Z]*){0,3}$)[a-zA-Z0-9]{5,10}$/;
    let regexPassword = /^(?=[^A-Z]*(?:[A-Z][^A-Z]*){0,3}$)[a-zA-Z0-9]{5,10}$/; 

    const form = document.getElementById("gameLogin"); 
    form.addEventListener("submit", function(event) {
        if (!validateForm()) {
        event.preventDefault();
        }
    });

    function validateForm(){
        let isValid = true; 
        const pseudo = document.getElementById("pseudo"); 
        const password = document.getElementById("password"); 
        const pseudoSpan = document.getElementById("pseudoSpan"); 
        const passwordSpan = document.getElementById("passwordSpan"); 

        const pseudoValue = pseudo.value.trim();
        if(!regexPseudo.test(pseudoValue)){
            pseudoSpan.textContent = "Veuillez entre un pseudo valide !"; 
            pseudoSpan.style.color = "red"; 
            isValid = false; 
        }
        else {
            pseudoSpan.textContent =""; 
        }
    
        const passwordValue = password.value.trim(); 
        if(!regexPassword.test(passwordValue)){
            passwordSpan.textContent = "Veuillez saisir un mot de passe valide !"; 
            passwordSpan.style.color = "red"; 
            isValid = false; 
        }
        else{
            passwordSpan.textContent =""; 
        }

        return isValid; 
    }   