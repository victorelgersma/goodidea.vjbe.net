<?php
if (!isset($page)) {
    $page = "";
}
?>
<!doctype html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <title>
        <?= $title ?? "A good ID(ea)" ?>
    </title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,100..900;1,9..144,100..900&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap">

    <link rel="stylesheet" href="style.css?v=1" />

    <?php if (!empty($chartjs)): ?>
        <script src="https://cdn.jsdelivr.net/npm/chart.js" defer></script>
    <?php endif; ?>

    <style>
        h1 {
            font-size: 4rem;
        }


        .id {
            font-family: Arial, Helvetica, sans-serif;
            font-weight: 700;
            color: #ff5c35;
            /* pick an accent color from your palette */
            letter-spacing: 0.05em;
        }
    </style>
</head>


<body>