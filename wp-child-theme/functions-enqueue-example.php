<?php
/**
 * Paste into SANGO child theme functions.php, after checking there is no existing PHP open tag here.
 * Enqueues archive/footer CSS only on category archive and always for footer.
 * Alternative: combine CSS in child-theme style.css and skip this snippet.
 */
add_action('wp_enqueue_scripts', function () {
    $rel = '/assets/css/mng-archive-footer.css';
    $path = get_stylesheet_directory() . $rel;
    if (file_exists($path)) {
        wp_enqueue_style(
            'mynewgear-archive-footer',
            get_stylesheet_directory_uri() . $rel,
            array(),
            (string) filemtime($path)
        );
    }
}, 30);
