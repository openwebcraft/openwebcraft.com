<?php

# Add my custom routes
return [
    
    # Add custom login url
    [
        'pattern' => 'login',
        'action'  => function () { return go('/panel'); }
    ],

    # Redirect home urls
    [
        'pattern' => '(:all)',
        'action'  => function($uid) {

            # If there's no page, try grab the post
            if ($page = site()->homePage()->find($uid))
                return site()->visit($page);

            # Else keep going
            $this->next();

        }    
    ],

    # Redirect old RSS link
    [
        'pattern' => 'feed',
        'action'  => function () { return go('/feed/rss'); }
    ],

    # Build the RSS Feed
    [
        'pattern' => 'feed/(rss|json)',
        'method'  => 'GET',
        'action'  => function ($type) {

            # Grab the collection of posts
            $posts = kirby()->collection('posts')->limit(10);

            # Set the options for the RSS feed
            $options = [
                'url'         => site()->url(),
                'title'       => site()->title() . ' Feed',
                'description' => 'Latest posts from the blog',
                'link'        => site()->url(),
                'datefield'   => 'published',
                'textfield'   => 'text',
                'snippet'     => r($type == 'rss' , 'feed/rss' , 'feed/json')
            ];

            # Return the feed
            return $posts->feed($options);
        }
    ]
];
