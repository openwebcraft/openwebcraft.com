<nav class="archive archive-posts">
    <h2 class="archive-title"><?= $site->archiveTitle()->html() ?></h2>
    <div class="archive-text"><?= $site->archiveText()->kt() ?></div>
    
    <div class="archive-latest">
        <h3 class="archive-subtitle archive-latest-subtitle"><?= $site->archivePreviewTitle()->html() ?></h3>
        <?php foreach ($posts as $p) : ?>
            <?php if ($p->published()->toDate('n') != $posts->first()->published()->toDate('n')) break; ?>
            <a class="archive-post-link <?php e($p->isActive() || $p == $post , 'archive-post-link-current') ?>" href="<?= url($p->uid()) ?>">
                <p class="archive-post-name"><?= $p->title()->html() ?></p>
                <hr class="archive-post-spacer">
                <p class="archive-post-day"><?= $p->published()->toDate('jS') ?></p>
            </a>
        <?php endforeach; ?>
    </div>
    
    <details>
        <summary><?= $site->archiveButtonText()->html() ?></summary>

    <?php

    // Year and Month Counter Variables
    $y = null;
    $m = null;

    foreach ($posts as $p) : ?>
        
        <?php if ($p->published()->toDate('n') == $posts->first()->published()->toDate('n')) continue; ?>

        <?php

        // Grab year and month from the current post
        $postY = $p->published()->toDate('Y');
        $postM = $p->published()->toDate('n');

        ?>

        <?php if ($postY != $y || $postM != $m) : ?>
            
            <h3 class="archive-subtitle">
            <?php if ($postY != $y) : ?>
                <span class='archive-year'><?= $postY ?></span>
            <?php endif; ?>
                <span class="archive-month"><?= strftime("%B" , $p->published()->toDate()) ?></span>
            </h3>

        <?php endif; ?>
        
            <a class="archive-post-link <?php e($p->isActive() || $p == $post , 'archive-post-link-current') ?>" href="<?= url($p->uid()) ?>">
                <p class="archive-post-name"><?= $p->title()->html() ?></p>
                <hr class="archive-post-spacer">
                <p class="archive-post-day"><?= $p->published()->toDate('jS') ?></p>
            </a>
        
        <?php

        // Update the month and year counter variables
        $y = $postY;
        $m = $postM;

        ?>       

    <?php endforeach ?>
    </details>
</nav>