<?php
$page = "comments";
$title = "Survey comments";

$json_file = __DIR__ . "/dashboard.json";

$data = json_decode(file_get_contents($json_file), true);

if ($data === null) {
    die("Invalid dashboard JSON.");
}

function h($value) {
    return htmlspecialchars((string)$value, ENT_QUOTES, "UTF-8");
}

$type = $_GET["type"] ?? "";

switch ($type) {
    case "q2":
        $title = "Other reasons";
        $comments = $data["q2_other"];
        break;

    case "q5":
        $title = "Comments";
        $comments = $data["q5_comments"];
        break;

    default:
        http_response_code(404);
        die("Unknown comment type.");
}

include "includes/header.php";
?>

<div class="wrap">

    <h2><?= h($title) ?></h2>

    <p>
        <a href="dashboard.php">← Back to dashboard</a>
    </p>

    <div class="comment-list full-page-comments">

        <?php if (count($comments) === 0): ?>

            <p>No comments.</p>

        <?php else: ?>

            <?php foreach ($comments as $comment): ?>

                <div class="comment-card">
                    <?= h("$comment") ?>
                </div>

            <?php endforeach; ?>

        <?php endif; ?>

    </div>

</div>