<?php

# All the visible posts
return function ($site) {
    return site()->homePage()->children()->listed()->sortBy('published' , 'desc');
};