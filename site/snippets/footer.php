        <?php if ($kirby->collection('menu')->isNotEmpty()) : ?>
        <footer class="footer">
            <nav class="footer-nav">
                <?php foreach ($kirby->collection('menu') as $item) : ?>
                <a class="footer-item" href="<?= $item->url() ?>"><?= ($item->menu()->isNotEmpty()) ? $item->menu()->html() : $item->title()->html() ?></a>
                <?php endforeach; ?>
            </nav>
        </footer>
        <?php endif; ?>
    </main>
</body>
</html>