// Function to filter table rows based on search input and date range
function filterTable() {
    var input, filter, table, tr, td, i, txtValue, startDate, endDate, dateValue;
    input = document.getElementById("search-input");
    filter = input.value.toUpperCase();
    startDate = new Date(document.getElementById("start-date").value);
    endDate = new Date(document.getElementById("end-date").value);
    table = document.getElementById("checkin-info-table");
    tr = table.getElementsByTagName("tr");

    for (i = 1; i < tr.length; i++) { // Start from 1 to skip the header row
        tr[i].style.display = "none"; // Hide the row initially

        // Check each cell in the row
        for (var j = 0; j < tr[i].cells.length; j++) {
            td = tr[i].cells[j];
            if (td) {
                txtValue = td.textContent || td.innerText;
                dateValue = new Date(tr[i].cells[3].innerText); // Assume date is in the 4th cell (index 3)
                if (
                    (txtValue.toUpperCase() === filter || filter === "") &&
                    (!isNaN(startDate) && dateValue >= startDate || isNaN(startDate)) &&
                    (!isNaN(endDate) && dateValue <= endDate || isNaN(endDate))
                ) {
                    tr[i].style.display = ""; // Show the row if it matches search and date criteria
                    break; // Stop checking other cells in this row
                }
            }
        }
    }
}
