// Assign constant symbols for currency values
const symbols = {
    GBP: "£",
    USD: "$",
    EUR: "€"
}

// Wait for entire page to load
document.addEventListener('DOMContentLoaded', function(){

    // Set currencySelect to currency select menu
    const currencySelect = document.querySelector("#currency");

    // Change all symbols on a page, if the symbol exists
    function applySymbol(code){
        const symbol = symbols[code];
        if (!symbol) return;

        // For every element of type currency symbol
        document.querySelectorAll(".currency-symbol").forEach(function (element){
            element.textContent = symbol;
        });
    }

    // Save the currency symbol choice on the users local storage
    const saved = localStorage.getItem("currency");
    if (saved && symbols[saved]){
        applySymbol(saved);
        // Only set the currency selected to saved IF the select menu exists
        if (currencySelect){
            currencySelect.value = saved;
        }
    }

    // Add listener on currency select menu, and change the symbol in the local storage and apply it
    currencySelect.addEventListener("change", function(){
        localStorage.setItem("currency", this.value);
        applySymbol(this.value);
    });
});