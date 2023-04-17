    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    
    <?php if (!$page->isHomePage() && $page->isUnlisted()) : ?>
    <!-- Robots Instructions -->
    <meta name="robots" content="noindex, nofollow">
    <?php endif; ?>

    <!-- RSS Links -->
    <link rel="alternate" type="application/rss+xml"  href="<?= site()->url() ?>/feed.rss"  title="<?= $site->title()->html() ?> RSS Feed">
    <link rel="alternate" type="application/json"     href="<?= site()->url() ?>/feed.json" title="<?= $site->title()->html() ?> JSON Feed">

    <!-- Descriptions -->
    <meta name="description" content="<?= $seo['desc'] ?>">

    <!-- Page Title -->
    <title><?= $seo['title'] ?></title>

