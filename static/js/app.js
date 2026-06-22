const rowsPerPage = 10;
let currentPage = 1;
let activeGroup = "all";
let activeSearch = "";

function leaderboardRows() {
    return Array.from(document.querySelectorAll("#leaderboardTable tbody tr"));
}

function rowMatches(row) {
    const name = row.cells[1].innerText.toLowerCase();
    const groupOk = activeGroup === "all" || row.dataset.group === activeGroup;
    const searchOk = !activeSearch || name.includes(activeSearch);
    return groupOk && searchOk;
}

function showPage(page) {
    const rows = leaderboardRows();
    if (!rows.length) return;

    const visibleRows = rows.filter(rowMatches);
    const totalPages = Math.max(1, Math.ceil(visibleRows.length / rowsPerPage));
    currentPage = Math.min(Math.max(page, 1), totalPages);

    rows.forEach(row => row.style.display = "none");
    visibleRows.forEach((row, index) => {
        const onPage = index >= (currentPage - 1) * rowsPerPage && index < currentPage * rowsPerPage;
        row.style.display = onPage ? "" : "none";
    });

    const pageInfo = document.getElementById("pageInfo");
    if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
}

function findMyRank() {
    const input = document.getElementById("myRankInput");
    const query = input ? input.value.trim().toLowerCase() : "";
    if (!query) return;

    let found = null;
    leaderboardRows().forEach(row => {
        const link = row.cells[1].querySelector("a");
        const name = link ? link.innerText.trim() : row.cells[1].innerText.split("\n")[0].trim();
        if (!found && name.toLowerCase().includes(query)) {
            found = {
                name,
                group: row.dataset.group || "",
                rankText: row.cells[0].innerText.trim(),
                points: row.cells[2].innerText.trim()
            };
        }
    });

    const resultEl = document.getElementById("myRankResult");
    if (!resultEl) return;

    if (!found) {
        resultEl.style.display = "none";
        alert("Name not found in the leaderboard. Try a different spelling.");
        return;
    }

    const rankNum = parseInt(found.rankText.replace(/\D/g, ""), 10);
    document.getElementById("mrName").textContent = found.name;
    document.getElementById("mrGroup").textContent = found.group;
    document.getElementById("mrPoints").textContent = found.points;
    document.getElementById("mrRank").textContent = rankNum ? `#${rankNum}` : found.rankText;

    const moveEl = document.getElementById("mrMove");
    if (rankNum <= 3) {
        moveEl.textContent = "🔥 Top 3!";
        moveEl.className = "rank-move up";
    } else if (rankNum <= 10) {
        moveEl.textContent = "⬆ Top 10";
        moveEl.className = "rank-move up";
    } else {
        moveEl.textContent = "Keep going!";
        moveEl.className = "rank-move same";
    }

    resultEl.style.display = "block";
    updateBadges(found.name);
}

function updateBadges(memberName) {
    let points = 0;
    leaderboardRows().forEach(row => {
        const link = row.cells[1].querySelector("a");
        const name = link ? link.innerText.trim() : "";
        if (name.toLowerCase() === memberName.toLowerCase()) {
            points = parseInt(row.cells[2].innerText.trim(), 10) || 0;
        }
    });

    const earned = {
        prayer: points >= 20,
        steps: points >= 15,
        hydration: points >= 25,
        screen: points >= 10,
        attendance: points >= 30
    };

    document.querySelectorAll(".badge-pill[data-badge]").forEach(pill => {
        const isEarned = earned[pill.dataset.badge];
        pill.classList.toggle("earned", isEarned);
        pill.classList.toggle("locked", !isEarned);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const rankInput = document.getElementById("myRankInput");
    if (rankInput) {
        rankInput.addEventListener("keyup", event => {
            if (event.key === "Enter") findMyRank();
        });
    }

    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("input", function () {
            activeSearch = this.value.trim().toLowerCase();
            showPage(1);
        });
    }

    document.querySelectorAll(".filter-btn").forEach(button => {
        button.addEventListener("click", function () {
            activeGroup = this.dataset.group;
            document.querySelectorAll(".filter-btn").forEach(btn => {
                btn.classList.remove("btn-primary");
                btn.classList.add("btn-outline-primary");
            });
            this.classList.remove("btn-outline-primary");
            this.classList.add("btn-primary");
            showPage(1);
        });
    });

    const prev = document.getElementById("prevPage");
    const next = document.getElementById("nextPage");
    if (prev) prev.addEventListener("click", () => showPage(currentPage - 1));
    if (next) next.addEventListener("click", () => showPage(currentPage + 1));

    showPage(1);

    document.querySelectorAll(".stat-card, .podium, .leaderboard, .panel").forEach((item, index) => {
        item.style.opacity = "0";
        item.style.transform = "translateY(16px)";
        setTimeout(() => {
            item.style.transition = "all .45s ease";
            item.style.opacity = "1";
            item.style.transform = "translateY(0)";
        }, index * 70);
    });
});
