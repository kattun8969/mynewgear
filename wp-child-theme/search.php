<?php
/**
 * SANGO child theme: search.php (search results)
 * Safe fallback: only affects search results; not posts or homepage.
 * Place in active child theme root after preview and backup.
 */
defined('ABSPATH') || exit;
get_header();
$term_name = '「' . get_search_query(false) . '」の検索結果';
$description = '';
?>
<main id="main" class="mng-archive-main" role="main">
  <header class="mng-archive-hero">
    <div class="mng-archive-container">
      <p class="mng-eyebrow">MY NEW GEAR / ARTICLES</p>
      <h1><?php echo esc_html($term_name); ?></h1>
      <?php if ($description) : ?><div class="mng-archive-description"><?php echo wp_kses_post($description); ?></div><?php endif; ?>

    </div>
  </header>
  <div class="mng-archive-container mng-archive-body">
  <?php if (have_posts()) : ?>
    <div class="mng-archive-grid" aria-label="記事一覧">
    <?php while (have_posts()) : the_post(); ?>
      <article <?php post_class('mng-archive-card'); ?>>
        <a class="mng-archive-card-link" href="<?php the_permalink(); ?>">
          <div class="mng-archive-thumb">
          <?php if (has_post_thumbnail()) : ?>
            <?php the_post_thumbnail('medium_large', array('loading' => 'lazy', 'alt' => get_the_title())); ?>
          <?php else : ?>
            <span class="mng-no-image">MY NEW GEAR</span>
          <?php endif; ?>
          </div>
          <div class="mng-archive-card-copy">
            <span class="mng-archive-kicker"><?php
              $cats_for_post = get_the_category();
              echo esc_html(!empty($cats_for_post) ? $cats_for_post[0]->name : '記事');
            ?></span>
            <h2><?php the_title(); ?></h2>
            <p><?php echo esc_html(wp_trim_words(get_the_excerpt(), 55, '…')); ?></p>
            <span class="mng-archive-date"><?php echo esc_html(get_the_date('Y.m.d')); ?></span>
          </div>
        </a>
      </article>
    <?php endwhile; ?>
    </div>
    <nav class="mng-archive-pages" aria-label="記事一覧ページ">
      <?php the_posts_pagination(array('mid_size' => 1, 'prev_text' => '前へ', 'next_text' => '次へ')); ?>
    </nav>
  <?php else : ?>
    <p>該当する記事がありません。別のキーワードでも検索してみてください。<a href="<?php echo esc_url(home_url('/')); ?>">トップページへ戻る</a></p>
  <?php endif; ?>
  </div>
</main>
<?php get_footer(); ?>
