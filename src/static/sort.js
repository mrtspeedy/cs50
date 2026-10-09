// Created with help of AI

// Wait for content on page to load
document.addEventListener("DOMContentLoaded", function () {
    const table = document.querySelector("#expense-table");
    if (!table) return;  // If the page has no expense table

    const tbody = table.querySelector("tbody");
    const headers = table.querySelectorAll("th[data-sort]");

    // Check what the current order method is, both the heading and direction
    let currentKey = "time";
    let direction = "desc";

    // For each heading of the table, check if it is the currently selected sorting value
    function updateArrows() {
        headers.forEach(function (th) {
            const arrow = th.querySelector(".sort-arrow");
            // If the current heading is the sorting value, show the arrow based on asc or desc order
            if (th.dataset.sort === currentKey) {
                arrow.textContent = direction === "asc" ? "▲" : "▼";
            } else {
                arrow.textContent = ""; // Else don't show an arrow on the heading
            }
        });
    }

    // Sort by the heading which was clicked
    function sortBy(th) {
        // The heading which to sort by
        const key = th.dataset.sort;
        // The data type of the sorting value
        const type = th.dataset.type;
        // Position of the header in the table
        const column = th.cellIndex;

        // Clicking the same column will flip the direction of the sort
        // Clicking another column will sort by ascending, by default
        if (key === currentKey) {
            direction = direction === "asc" ? "desc" : "asc";
        } else {
            currentKey = key;
            direction = "asc";
        }

        // Turn the rows into an array so it can be sorted
        const rows = Array.from(tbody.querySelectorAll("tr"));

        // Compare the rows by raw value and not the formatted text
        rows.sort(function (a, b) {
            const x = a.cells[column].dataset.value;
            const y = b.cells[column].dataset.value;

            let result;

            // Compare by number else compare by text, ignoring case
            if (type === "number") {
                result = parseFloat(x) - parseFloat(y);
            } else {
                result = x.localeCompare(y, undefined, { sensitivity: "base" });
            }

            // Flip the result when sorting by descending
            return direction === "asc" ? result : -result;
        });

        // Put all rows into their new order
        rows.forEach(function (row) {
            tbody.appendChild(row);
        });

        // Refresh the arrows based on the new sort
        updateArrows();
    }

    // Make all headers clickable so you can sort by them
    headers.forEach(function (th) {
        th.addEventListener("click", function () {
            sortBy(th);
        });
    });

    // Shows the default sort order (time)
    updateArrows();
});