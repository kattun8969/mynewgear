<?php
/**
 * SANGO child theme: category.php (MyNewGear article category archives)
 * Safe fallback: this template only affects category archives; not posts, search, tags or homepage.
 * Place in active child theme root after preview and backup.
 */
defined('ABSPATH') || exit;
get_header();
$term = get_queried_object();
$term_name = ($term && !is_wp_error($term)) ? single_cat_title('', false) : '記事一覧';
$description = category_description();
?>
<main id="main" class="mng-archive-main" role="main">
  <header class="mng-archive-hero">
    <div class="mng-archive-container">
      <p class="mng-eyebrow">MY NEW GEAR / ARTICLES</p>
      <h1><?php echo esc_html($term_name); ?></h1>
      <?php if ($description) : ?><div class="mng-archive-description"><?php echo wp_kses_post($description); ?></div><?php endif; ?>
      <nav class="mng-archive-shortcuts" aria-label="記事カテゴリ">
        <?php
        $top = get_category_by_slug('gear');
        $cats = $top ? get_categories(array('parent' => (int) $top->term_id, 'hide_empty' => false)) : array();
        if ($top) {
          echo '<a href="' . esc_url(get_category_link($top)) . '" class="' . ((int) $term->term_id === (int) $top->term_id ? 'is-current' : '') . '">ギター機材</a>';
        }
        foreach ($cats as $cat) {
          echo '<a href="' . esc_url(get_category_link($cat)) . '" class="' . ((int) $term->term_id === (int) $cat->term_id ? 'is-current' : '') . '">' . esc_html($cat->name) . '</a>';
        }
        ?>
      </nav>
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
    <p>現在、このカテゴリには記事がありません。<a href="<?php echo esc_url(home_url('/')); ?>">トップページへ戻る</a></p>
  <?php endif; ?>
  </div>
</main>
<?php get_footer(); ?>
