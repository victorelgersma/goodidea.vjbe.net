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
    <h1 class="left" style="font-family: cursive">
        good <br> <span class="id" style="font-family: Baskerville">ID</span>ea
    </h1>
    <img src="https://img.vjbe.net/phone.svg" height="100px" alt="Illustration of a smartphone" />

</header>

<div class="wrap">


    <section class="hero">

        <p class="hero-tagline">
            A student-led campaign to re-introduce an (optional) physical student card alongside the existing <a
                href="https://students.uu.nl/en/practical-information/enrolment/student-card" target="_blank"
                rel="noopener"> digital student card</a>, at the Universiteit Utrecht.
        </p>


        <div class="hero-actions">

            <a class="button primary" href="/dashboard.php">
                View survey results
            </a>

            <a class="button secondary" href="https://survey.uu.nl/jfe/form/SV_eWjarcbWuvJP2Z0" target="_blank"
                rel="noopener">
                Fill in the survey
            </a>

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


    </section>



    <div class="card">

        <h2>
            Why an (optional) physical ID?
        </h2>

        <p>
            Since the 1 June 2017, Utrecht University stopped providing a physical student card, becoming the first and
            only university in the Netherlands to have a digital-only student card policy. Students who prefer not to
            carry a smartphone
            with an internet connection are asked to <a
                href="https://students.uu.nl/en/practical-information/enrolment/digital-student-card/frequently-asked-questions"
                target="_blank" rel="noopener">print
                out a certificate of enrollment </a> using OSIRIS, which has proven to be an inconvenient alternative as
            it is cumbersome to carry and often not recognized in practice.
        </p>
        <p>
            We believe students should be able to choose how they identify themselves. Offering only a digital student
            card effectively requires students to carry an internet-connected device, even when a physical card would
            better suit their needs.
        </p>

        <p>Our <a href="/dashboard.php">survey</a> shows that students broadly support the re-introduction of an optional physical student card and are even willing to pay a small fee to cover the cost </p>

    </div>


    <div class="card">

        <h2>
            How can I help?
        </h2>

        <p>Are you interested in helping the campaign? Great! Here are some ways to help us:</p>
        <ul>

            <li>
                E-mail the university council (U-raad) at <a href="mailto:studentenuraad@uu.nl">studentenuraad@uu.nl</a>
                and explain why this issue matters to you.
            </li>

            <li>
                Fill in our <a href="https://card.vjbe.net/survey">online survey </a> and encourage others to do so.
            </li>
            <ul>


                <li>
                    Prefer not to fill out an online form? You can print out a <a
                        href="https://samizdat.vjbe.net/2026-08-04-Enqu%C3%AAte%20Studentenkaart.pdf"> Dutch </a> or <a
                        href="https://samizdat.vjbe.net/2026-08-04-Student%20Card%20Survey.pdf"> English</a> version of
                    our survey, fill it out, and send a scan to <a
                        href="mailto:agoodidea@vjbe.net">agoodidea@vjbe.net</a>
                </li>
            </ul>

            <li>
                Share this website with your UU-friends!
            </li>
            <li> Follow us on instagram <a href="https://www.instagram.com/good.id.ea/">@good.id.ea</a>!</li>
           
        </ul>

    </div>

         <div class="card">

                <h2>
                    Need a physical card right now?
                </h2>

                <p>
                    While we campaign for an official optional physical student card,
                    we have created an unofficial convenience card: a pocket-sized
                    laminated copy of your enrollment certificate.
                </p>

                <p>
                    It is not issued by Utrecht University and is not a replacement for
                    an official student card. However, it can make it easier to carry
                    proof of your student status without folding around an A4 printout.
                </p>

                <p>
                    You can request one here:
                    <a href="https://studentcard.vjbe.net">
                        Unofficial Convenience Card
                    </a>
                </p>

            </div>


</div>


<?php include "includes/footer.php"; ?>