
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

    <?php if (!empty($chartjs)): ?>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <?php endif; ?>

    <link rel="stylesheet" href="style.css" />
</head>

<body>
