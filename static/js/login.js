    let regexPseudo = /^(?=[^A-Z]*(?:[A-Z][^A-Z]*){0,3}$)[a-zA-Z0-9]{5,10}$/;
    let regexPassword = /^[A-Z][a-z]{7,12}\d{2}$/; 

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
            pseudoSpan.textContent = "Veuillez entrer un pseudo valide !";
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

// ===== POPUP RÈGLES =====
const regexPseudoLength = /^.{5,10}$/;
const regexPseudoChars  = /^[a-zA-Z0-9]+$/;
const regexPseudoUpper  = /^[^A-Z]*([A-Z][^A-Z]*){0,3}$/;

const regexPwdUpper  = /^[A-Z]/;
const regexPwdLower  = /^[A-Z][a-z]{7,12}/;
const regexPwdDigits = /^.+\d{2}$/;

const rules = [
    {
        input: "pseudo",
        popup: "pseudoRules",
        checks: [
            { id: "rule-pseudo-length", regex: regexPseudoLength },
            { id: "rule-pseudo-chars",  regex: regexPseudoChars  },
            { id: "rule-pseudo-upper",  regex: regexPseudoUpper  }
        ]
    },
    {
        input: "password",
        popup: "passwordRules",
        checks: [
            { id: "rule-pwd-upper",  regex: regexPwdUpper  },
            { id: "rule-pwd-lower",  regex: regexPwdLower  },
            { id: "rule-pwd-digits", regex: regexPwdDigits }
        ]
    }
];

rules.forEach(({ input, popup, checks }) => {
    const inputEl = document.getElementById(input);
    const popupEl = document.getElementById(popup);

    inputEl.addEventListener("focus", () => popupEl.classList.add("visible"));
    inputEl.addEventListener("blur",  () => popupEl.classList.remove("visible"));
    inputEl.addEventListener("input", () => {
        const v = inputEl.value;
        checks.forEach(({ id, regex }) =>
            document.getElementById(id).classList.toggle("valid", v.length > 0 && regex.test(v))
        );
    });
});