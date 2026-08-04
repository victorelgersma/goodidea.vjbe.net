<?php
$page = "home";
$title = "A good ID(ea) – Optional physical student card";

$json_file = __DIR__ . "/dashboard.json";

$responses = null;

if (file_exists($json_file)) {
    $data = json_decode(
        file_get_contents($json_file),
        true
    );

    if ($data && isset($data["meta"]["total_kept"])) {
        $responses = $data["meta"]["total_kept"];
    }
}

?>

<?php include "includes/header.php"; ?>


<div class="wrap">


    <section class="hero">

        <p class="hero-tagline">
            A student-led campaign to introduce a physical student card alongside the <a
                href="https://students.uu.nl/en/practical-information/enrolment/student-card"> digital one</a>, at the Universiteit Utrecht. 
        </p>


        <div class="hero-actions">

            <a class="button primary" href="/dashboard.php">
                View survey results
            </a>

            <a class="button secondary" href="https://survey.uu.nl/jfe/form/SV_eWjarcbWuvJP2Z0">
                Fill in the survey
            </a>

        </div>


    </section>



    <div class="card">

        <h2>
            Why this project?
        </h2>

        <p>
            The University currently provides a digital-only student card. Students who do not possess a smartphone with
            a 4G connection are asked to <a
                href="https://students.uu.nl/en/practical-information/enrolment/digital-student-card/frequently-asked-questions">print
                out a certificate of enrollment </a> using OSIRIS, which is an inconvenient alternative as it is
            cumbersome to carry and often not recognized in practice.
        </p>
        <p>
            We believe it is inappropriate for a university to require students to carry an internet-connected device
            with them at all times.
        </p>
        <p>
            Students <a href="/dashboard.php"> overwhelmingly favour </a> the reintroduction of an optional physical
            student card and are even prepared to pay a small fee for it.
        </p>


    </div>


    <div class="card">

        <h2>
            How can I help?
        </h2>

        <p>Are you interested in helping the campaign? Great! Here are some ways to help us:</p>
        <ul>

            <li>E-mail the university council (U-raad) at <a mailto="studentenuraad@uu.nl">studentenuraad@uu.nl</a> and tell them you care about this issue, and why. 
            </li>

            <li>fill in our <a href="card.vjbe.net/survey">survey </a> and encourage others to do so</li>
        </ul>

    </div>


    <?php if ($responses !== null): ?>

        <div class="summary">

            <span class="count">
                <?= htmlspecialchars($responses) ?>
            </span>

            <span class="label">
                valid survey responses collected
            </span>

        </div>

    <?php endif; ?>


</div>


<?php include "includes/footer.php"; ?>