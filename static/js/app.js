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

// ==============================
// Pagination
// ==============================

const rowsPerPage = 10;
let currentPage = 1;

function getVisibleRows() {
    return Array.from(
        document.querySelectorAll("#leaderboardTable tbody tr")
    ).filter(row => row.dataset.filter !== "hidden");
}

function showPage(page) {

    const rows = getVisibleRows();

    const totalPages = Math.max(1, Math.ceil(rows.length / rowsPerPage));

    if (page < 1) page = 1;
    if (page > totalPages) page = totalPages;

    currentPage = page;

    document.querySelectorAll("#leaderboardTable tbody tr").forEach(r=>{
        if(r.dataset.filter==="hidden"){
            r.style.display="none";
        }
    });

    rows.forEach((row,index)=>{

        row.style.display =
            (index >= (page-1)*rowsPerPage &&
             index < page*rowsPerPage)
            ? ""
            : "none";

    });

    document.getElementById("pageInfo").innerHTML =
        "Page " + currentPage + " of " + totalPages;

}

document.getElementById("prevPage").onclick=function(){

    showPage(currentPage-1);

}

document.getElementById("nextPage").onclick=function(){

    showPage(currentPage+1);

}

document.querySelectorAll(".filter-btn").forEach(btn=>{

    btn.addEventListener("click",function(){

        const group=this.dataset.group;

        document.querySelectorAll("#leaderboardTable tbody tr").forEach(row=>{

            if(group==="all"){

                row.dataset.filter="show";

            }else{

                row.dataset.filter =
                    row.dataset.group===group
                    ? "show"
                    : "hidden";

            }

        });

        currentPage=1;

        showPage(1);

    });

});

showPage(1);

document.querySelectorAll(".view-profile").forEach(btn => {

    btn.addEventListener("click", function () {

        document.getElementById("profileName").textContent = this.dataset.name;
        document.getElementById("profileGP").textContent = this.dataset.gp;
        document.getElementById("profileRank").textContent = this.dataset.rank;
        document.getElementById("profilePoints").textContent = this.dataset.points;

        document.getElementById("profileSteps").textContent = this.dataset.steps;
        document.getElementById("profileExercise").textContent = this.dataset.exercise;
        document.getElementById("profileWater").textContent = this.dataset.water;
        document.getElementById("profileSleep").textContent = this.dataset.sleep;
        document.getElementById("profilePrayer").textContent = this.dataset.prayer;

        new bootstrap.Modal(document.getElementById("profileModal")).show();

    });

});