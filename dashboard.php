
<?php
$page = "results";
$title = "Results – A good ID(ea)";
$chartjs = true;

$json_file = __DIR__ . "/dashboard.json";

if (!file_exists($json_file)) {
    die("Dashboard data not found. Run compile_dashboard.sh first.");
}

$data = json_decode(
    file_get_contents($json_file),
    true
);

if ($data === null) {
    die("Invalid dashboard JSON.");
}

function h($value) {
    return htmlspecialchars(
        (string)$value,
        ENT_QUOTES,
        "UTF-8"
    );
}

?>

<?php include "includes/header.php"; ?>


<div class="wrap">


<header class="page-header">
    <p class="back-home">
    <a href="index.php">← Back home</a>
</p>

    <h2>
        Student responses regarding an optional physical student card
    </h2>

    <p> <a href="results_anonymized.csv" download> Download the anonymised survey data ↓ </a> </p>

</header>


<div class="summary">

    <span class="count">
        <?= h($data["meta"]["total_kept"]) ?>
    </span>

    <span class="label">
        valid responses
    </span>

</div>



<div class="grid">


<!-- Q1 -->

<div class="card" data-qnum="Q1">

<h2>
<?= h($data["questions"]["Q1"]) ?>
</h2>

<p class="sub">
Would students request an optional physical card?
</p>

<div class="chart-box">
<canvas id="q1Chart"></canvas>
</div>

</div>



<!-- Q2 -->

<div class="card full" data-qnum="Q2">

<h2>
<?= h($data["questions"]["Q2"]) ?>
</h2>

<p class="sub">
<?= h($data["q2"]["answered"]) ?> respondents selected at least one reason · multiple selections allowed
</p>

<div class="reason-list tall" id="q2Reasons"></div>

</div>

<!-- Q2 other -->

<div class="card full">

<h2>Other reasons</h2>

<a class="mobile-comments-link"
   href="comments.php?type=q2">
    View all <?= count($data["q2_other"]) ?> responses →
</a>

<div class="comment-list desktop-only">

<?php foreach ($data["q2_other"] as $comment): ?>

<div class="comment-card">
<?= h($comment) ?>
</div>

<?php endforeach; ?>

</div>

</div>


<!-- Q4 -->

<div class="card" data-qnum="Q4">

<h2>
<?= h($data["questions"]["Q4"]) ?>
</h2>



<div class="chart-box">
<canvas id="q4Chart"></canvas>
</div>

</div>



<!-- Q16 -->

<div class="card" data-qnum="Q16">

<h2>
<?= h($data["questions"]["Q16"]) ?>
</h2>

<p class="sub">
Amount respondents would pay
</p>


<div class="chart-box">
<canvas id="q16Chart"></canvas>
</div>


</div>






<!-- Comments -->

<div class="card full">

<h2>
<?= h($data["questions"]["Q5"]) ?>
</h2>

<a class="mobile-comments-link"
   href="comments.php?type=q5">
    View all <?= count($data["q5_comments"]) ?> comments →
</a>

<div class="comment-list desktop-only">

<?php if (count($data["q5_comments"]) === 0): ?>

<p class="empty-msg">
No comments submitted.
</p>

<?php else: ?>

<?php foreach ($data["q5_comments"] as $comment): ?>

<div class="comment-card">
<?= h($comment) ?>
</div>

<?php endforeach; ?>

<?php endif; ?>

</div>

</div>




<!-- Contacts -->

<div class="card full">

<h2>
Optional contact details
</h2>


<div class="contact-row">

<div class="contact-pill">
Names provided:
<?= h($data["contacts"]["names"]) ?>
</div>


<div class="contact-pill">
Emails provided:
<?= h($data["contacts"]["emails"]) ?>
</div>

</div>

</div>


</div>


<div class="methodology">

<h3>
Methodology
</h3>

<p>
Responses below 50% completion
were excluded. Total submissions:
<?= h($data["meta"]["total_submissions"]) ?>.
Excluded incomplete:
<?= h($data["meta"]["incomplete_excluded"]) ?>.
</p>

</div>



</div>



<script>

const dashboard = <?= json_encode($data, JSON_UNESCAPED_UNICODE); ?>;


function makeChart(id, labels, values, type="doughnut") {

    new Chart(
        document.getElementById(id),
        {
            type: type,

            data: {
                labels: labels,

                datasets: [{
                    data: values,

                    backgroundColor: [
                        "#4f46e5",
                        "#f59e0b",
                        "#ef4444",
                        "#94a3b8",
                        "#22c55e",
                        "#8b5cf6",
                        "#06b6d4",
                    ]
                }]
            },

            options: {
                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        }
    );
}



makeChart(
    "q1Chart",
    dashboard.q1.labels,
    dashboard.q1.counts
);


const q2Container = document.getElementById("q2Reasons");

const maxQ2 = Math.max(...dashboard.q2.counts);

dashboard.q2.labels.forEach((label, i) => {

    const row = document.createElement("div");
    row.className = "reason-row";

    const percent = (dashboard.q2.counts[i] / maxQ2) * 100;

    row.innerHTML = `
        <div class="reason-label">${label}</div>

        <div class="reason-bar-wrap">
            <div class="reason-bar" style="width:${percent}%"></div>
        </div>

        <div class="reason-count">
            ${dashboard.q2.counts[i]}
        </div>
    `;

    q2Container.appendChild(row);

});


makeChart(
    "q4Chart",
    dashboard.q4.labels,
    dashboard.q4.counts
);


new Chart(
    document.getElementById("q16Chart"),
    {
        type: "bar",

        data: {
            labels: dashboard.q16.labels,

            datasets: [{
                data: dashboard.q16.counts,
                backgroundColor: "#4f46e5",
                borderRadius: 4
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false
                }
            },

            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    }
);


</script>



<?php include "includes/footer.php"; ?>