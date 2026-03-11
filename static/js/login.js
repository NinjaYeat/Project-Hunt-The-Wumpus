let regexPseudo = /^(?=[^A-Z]*(?:[A-Z][^A-Z]*){0,3}$)[a-zA-Z0-9]{5,10}$/;
let regexPassword = /^[A-Z][a-z]{7,12}\d{2}$/;


let form = document.getElementById("gameLogin") || document.getElementById("gameRegister");
if (form) {
    form.addEventListener("submit", function(event) {
        if (!validateForm()) {
            event.preventDefault();
        }
    });
}

function validateForm() {
    let isValid = true;
    let pseudo = document.getElementById("pseudo");
    let password = document.getElementById("password");
    let pseudoSpan = document.getElementById("pseudoSpan");
    let passwordSpan = document.getElementById("passwordSpan");

    if (!pseudo || !password) return true;

    let pseudoValue = pseudo.value.trim();
    if (!regexPseudo.test(pseudoValue)) {
        if (pseudoSpan) {
            pseudoSpan.textContent = "Veuillez entrer un pseudo valide !";
            pseudoSpan.style.color = "red";
        }
        isValid = false;
    } else {
        if (pseudoSpan) pseudoSpan.textContent = "";
    }

    let passwordValue = password.value.trim();
    if (!regexPassword.test(passwordValue)) {
        if (passwordSpan) {
            passwordSpan.textContent = "Veuillez saisir un mot de passe valide !";
            passwordSpan.style.color = "red";
        }
        isValid = false;
    } else {
        if (passwordSpan) passwordSpan.textContent = "";
    }

    return isValid;
}

// ===== POPUP RÈGLES =====
let regexPseudoLength = /^.{5,10}$/;
let regexPseudoChars  = /^[a-zA-Z0-9]+$/;
let regexPseudoUpper  = /^[^A-Z]*([A-Z][^A-Z]*){0,3}$/;

let regexPwdUpper  = /^[A-Z]/;
let regexPwdLower  = /^[A-Z][a-z]{7,12}/;
let regexPwdDigits = /^.+\d{2}$/;

let rules = [
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
    let inputEl = document.getElementById(input);
    let popupEl = document.getElementById(popup);

    // si sur login on ne crash pas
    if (!inputEl || !popupEl) return;

    inputEl.addEventListener("focus", () => popupEl.classList.add("visible"));
    inputEl.addEventListener("blur",  () => popupEl.classList.remove("visible"));
    inputEl.addEventListener("input", () => {
        let v = inputEl.value;
        checks.forEach(({ id, regex }) => {
            let li = document.getElementById(id);
            if (!li) return;
            li.classList.toggle("valid", v.length > 0 && regex.test(v));
        });
    });
});