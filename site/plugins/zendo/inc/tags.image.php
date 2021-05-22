<?php

# Custom Image Kirbytags
return [

    # All the available attributes
    'attr' => [
        'alt',
        'caption',
        'class',
        'height',
        'imgclass',
        'link',
        'linkclass',
        'rel',
        'target',
        'text',
        'title',
        'width',
        'loading',
        'decoding'
    ],

    # Return the markup
    'html' => function ($tag) {

        # Covert the value to a url
        $tag->src      = Url::to($tag->value);
        $tag->imgclass = $tag->imgclass ? 'img ' . $tag->imgclass : 'img';

        # Add lazy loading and decoding
        $tag->loading  = "lazy";
        $tag->decoding = "async";

        # If the file is pointing to local file do the rest
        if ($tag->file    = $tag->file($tag->value)) :
            $tag->src     = $tag->file->url();
            $tag->alt     = $tag->alt     ?? $tag->file->alt()->or(' ')->value();
            $tag->title   = $tag->title   ?? $tag->file->title()->value();
            $tag->caption = $tag->caption ?? $tag->file->caption()->value();
        else:
            $tag->src = Url::to($tag->value);
        endif;

        # Add the link if needed
        $link = function ($img) use ($tag) {

            # If there's no link return the image
            if (empty($tag->link) === true) return $img;

            # Set the value of the link
            $link = $tag->link === 'self' ? $tag->src : $tag->link;

            # If the original value is equal to the file url set the as the value
            if ($link = $tag->file($tag->link)) $link = $link->url();

            return Html::a($link, [$img], [
                'rel'    => $tag->rel,
                'class'  => $tag->linkclass,
                'target' => $tag->target
            ]);

        };

        # Generate the image tag
        $image = Html::img($tag->src, [
            'width'    => $tag->width,
            'height'   => $tag->height,
            'class'    => $tag->imgclass,
            'title'    => $tag->title,
            'alt'      => $tag->alt ?? ' ',
            'loading'  => $tag->loading,
            'decoding' => $tag->decoding
        ]);

        # If the option is set for the kirbytext use that option
        if ($tag->kirby()->option('kirbytext.image.figure', true) === false)
            return $link($image);

        # Render KirbyText in caption
        if ($tag->caption)
            $tag->caption = [$tag->kirby()->kirbytext($tag->caption, [], true)];

        # Images will be all absolute positioned to allow for a better loading experience
        # Don't do this if the image is loaded from an external source
        if ($tag->file($tag->value))
            $tag->padding = $tag->file->thePadding()->isNotEmpty() ? $tag->file->thePadding() . "%" : $tag->file->height() / $tag->file->width() * 100 . "%";

        # Create a div and place the image inside it
        $wrapper = Html::tag('div' , [ $link($image) ], [
            'class' => 'img-wrapper',
            'style' => "padding-bottom: {$tag->padding}"
        ]);

        # If the image is portrait do the magic
        if ($tag->file->orientation() == 'portrait' && $tag->file->withTemplate()->isTrue()) :
            
            # Calculate the width
            $width = $tag->file->thePadding()->isNotEmpty() ? 80 / ($tag->file->theHeight()->value() / $tag->file->theWidth()->value())  : 80 / ($tag->file->height() / $tag->file->width());
            
            $wrapper = Html::tag('div' , [ $link($image) ], [
                'class' => 'img-wrapper',
                'style' => "height:80vmin; width:{$width}vmin;"
            ]);
        endif;

        # Settings for the figure
        $tag->figureSettings = [
            'class' => 'img-figure',
            'data-template' => $tag->file->withTemplate()->isFalse() ? 'without' : 'with'
        ];

        # If there's a width set, add the witdh as an inline style
        if ($tag->width)
            $tag->figureSettings['style'] = "max-width:{$tag->width}px";

        # The new extra container
        $container = Html::tag('div' , [$wrapper] , ['class' => 'img-container']);
        
        # Return the figure
        return Html::figure([ $container ], $tag->caption, $tag->figureSettings);
    }

];