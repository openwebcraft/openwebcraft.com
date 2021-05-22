<?php

# Listed pages to be displayed in the footer
return function ($site) {
    return site()->children()->listed()->sortBy('num' , 'asc');
};