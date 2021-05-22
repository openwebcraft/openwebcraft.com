<?php

# Custom Link Tag
return [

    # All the available attributes
    'attr' => [
        'class',
        'lang',
        'rel',
        'role',
        'target',
        'text',
        'title'
    ],

    # Generate the desired html
    'html' => function($tag) {

        # Lang check
        if (empty($tag->lang) === false)
            $tag->value = Url::to($tag->value, $tag->lang);

        # If the link is internal
        if (Str::contains($tag->value , 'http') && !Str::contains($tag->value , kirby()->site()->url()))
            $tag->target = "_blank";

        # Return the link
        return Html::a($tag->value, $tag->text, [
            'rel'    => $tag->rel,
            'class'  => $tag->class,
            'role'   => $tag->role,
            'title'  => $tag->title,
            'target' => $tag->target,
        ]);
    }
];