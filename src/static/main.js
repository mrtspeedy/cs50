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

    // Add listener on currency select menu
    currencySelect.addEventListener("change", function(){

        // Set the symbol to the value it was changed to
        const symbol = symbols[this.value];

        // Go through entire page and change all currency symbols to the one there is now
        document.querySelectorAll(".currency-symbol").forEach(function(element){
            element.textContent = symbol;
        });
    });
});