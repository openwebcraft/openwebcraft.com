<?php

# All the custom controllers
return [

    'seo' => function ($page, $pages, $site, $kirby) {

        # Define the two basic seo tags    
        $seo_title = r($page->isHomePage(), $site->title()->html() . ' – ' . $site->subtitle()->html(), $page->title()->html() . ' – ' . $site->title()->html());
        $seo_description  = r($page->isHomePage(), $site->description(), $page->text()->excerpt(150));

        # Return the content
        return compact('seo_title', 'seo_description');
    }
];
