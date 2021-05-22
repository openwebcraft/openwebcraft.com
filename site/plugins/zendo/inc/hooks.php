<?php

# Return an array with all the custom actions attached to the hooks
return [
    
    # Resize the image on upload
    'file.create:after' => function ($file) {
        
        # if the file is not resizable abort
        if (!$file->isResizable())
            return true;

        # Exit if we're not working with a web image
        if (!in_array($file->extension() , ['gif' , 'jpg' , 'jpeg' , 'png']))
            return true;

        # If the file is smaller than the minimum file size abort
        if ($file->width() <= option('manu.zendo.maxWidth'))
            return true;

        # Try resizing the image on upload
        try {
            kirby()->thumb($file->root(), $file->root(), [ 'width' => option('manu.zendo.maxWidth') ]);
        } catch (Exception $e) {
            throw new Exception($e->getMessage());
        }
    },

    # Attach the size of the image and the ratio to the image txt file
    'file.create:after' => function ($file) {

        # Exit if we're not working with a web image
        if (!in_array($file->extension() , ['gif' , 'jpg' , 'jpeg' , 'png']))
            return true;

        // Add the relevant meta info
        return $file->update([
            'theWidth'   => $file->width(),
            'theHeight'  => $file->height(),
            'thePadding' => 100 / $file->width() * $file->height(),
        ]);

    },

    # Run the same code on resize
    'file.replace:after' => function ($newFile, $oldFile) {
        kirby()->trigger('file.create:after', $newFile);
    },


    # Fix the () nested inside the kirbytags
    'kirbytags:before' => function ($text, array $data = [], array $options = []) {

        # @rasteiner come up with this monster right here, don't blame me if your server explodes
        $regex = '/\(\s*(\w+?):\s*?\w+?\s*?(?:\w+?:(?\'rec\'[:;]-?[\(\)]|[^)(]+?|\((?&rec)*?\))*?)*?\)/mx';

        # KirbyTags have not been parsed at this point
        $text = preg_replace_callback($regex, function ($matches) {
            
            # Loop through each tag and perform a replace
            foreach ($matches as $match) :

                # First trim the () at the beginning and at the end of the tag,
                # because we want to keep those
                $match = substr($match , 1 , -1);

                # Then look for () inside the string and replace them with another character
                $match = str_replace(['(',')'] , ['⎣','⎦'] , $match);

                # Add back the two () at the beginning and the end
                $match = "({$match})";

                # Return the string
                return $match;

            endforeach;

            # Return al the kirbytags
            return $matches;

        }, $text);

        return $text;
    },

    # Add back the () we swapped previously
    'kirbytags:after' => function ($text, array $data = [], array $options = []) {
        $text = str_replace(['⎣','⎦'] , ['(',')'] , $text);
        return $text;
    }
];
