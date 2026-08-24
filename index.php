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


<header class="flex">
    <h1 class="left goodidea">
        <span class="good">good</span>

        <span class="idea">
            <span class="id">ID</span><span>ea</span>
        </span>
    </h1>
    <img src="https://img.vjbe.net/phone.svg" height="100" alt="" />

</header>

<div class="wrap">

    <section class="hero">

        <div class="hero-actions">


            <a class="button secondary" href="/about.php">
                About
            </a>

            <a class="button primary" href="https://survey.uu.nl/jfe/form/SV_eWjarcbWuvJP2Z0" target="_blank"
                rel="noopener">
                Fill in the survey!
            </a>
            <a class="button secondary" href="/dashboard.php">
                View results
            </a>
        </div>
    </section>

</div>


<?php include "includes/footer.php"; ?>