// ==============================
// Search Leaderboard
// ==============================

const searchInput = document.getElementById("searchInput");

if (searchInput) {

    searchInput.addEventListener("keyup", function () {

        const filter = this.value.toUpperCase();

        const rows = document.querySelectorAll("#leaderboardTable tbody tr");

        rows.forEach(row => {

            const name = row.cells[1].innerText.toUpperCase();

            row.style.display = name.includes(filter) ? "" : "none";

        });

    });

}

// ==============================
// Fade In Animation
// ==============================

window.addEventListener("load", () => {

    document.querySelectorAll(".stat-card, .podium, .leaderboard").forEach((item, index) => {

        item.style.opacity = "0";
        item.style.transform = "translateY(20px)";

        setTimeout(() => {

            item.style.transition = "all .6s ease";
            item.style.opacity = "1";
            item.style.transform = "translateY(0)";

        }, index * 150);

    });

});

// ==============================
// Auto Refresh Every 30 Seconds
// ==============================

setInterval(() => {

    console.log("Refreshing leaderboard...");

    location.reload();

}, 30000);
// ==============================
// Age Group Filter
// ==============================

document.querySelectorAll(".filter-btn").forEach(button => {

    button.addEventListener("click", function () {

        const group = this.dataset.group;

        document.querySelectorAll(".filter-btn").forEach(btn => {

            btn.classList.remove("btn-primary");
            btn.classList.add("btn-outline-primary");

        });

        this.classList.remove("btn-outline-primary");
        this.classList.add("btn-primary");

        document.querySelectorAll("#leaderboardTable tbody tr").forEach(row => {

            if (group === "all") {

                row.style.display = "";

            } else {

                row.style.display =
                    row.dataset.group === group ? "" : "none";

            }

        });

    });

});