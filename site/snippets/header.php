<!DOCTYPE html>
<html lang="en">
<head>

<?= snippet('header/meta')  ?>
<?= snippet('header/icons') ?>
    
<?= css($kirby->url('assets') . '/css/main.min.css') ?>

<?= css($kirby->url('assets') . '/css/hljs-zenburn.css') ?>


</head>

<body class="<?= "page-{$page->intendedTemplate()}" ?>">
    <main class="main">
