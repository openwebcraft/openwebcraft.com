<?php

# Titles
$metaTitle = r($page->isHomePage() , "{$site->title()->html()} – {$site->subtitle()->html()}" , "{$page->title()->html()} – {$site->title()->html()}");
$metaDesc  = r($page->text()->isNotEmpty() , $page->text()->excerpt(140) , $site->text()->excerpt(140));


?>

    <!-- Descriptions -->
    <meta content="<?= $metaDesc ?>" name="description">

    <!-- Page Title -->
    <title><?= $metaTitle ?></title>
