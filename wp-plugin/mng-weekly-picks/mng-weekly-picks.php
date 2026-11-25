<?php
/**
 * Plugin Name: MyNewGear Weekly Picks
 * Description: Editorially curated weekly gear picks. Revenue attribution stays in Pochipp.
 * Version: 0.1.0
 * Requires PHP: 7.4
 */
defined('ABSPATH') || exit;

add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('mng-weekly-picks', plugins_url('style.css', __FILE__), array(), '0.1.0');
});

add_action('init', function () {
    register_post_type('mng_gear', array(
        'labels' => array('name' => '注目機材', 'singular_name' => '機材', 'add_new_item' => '機材を追加'),
        'public' => false,
        'show_ui' => true,
        'show_in_menu' => true,
        'menu_icon' => 'dashicons-star-filled',
        'supports' => array('title', 'thumbnail', 'excerpt'),
        'capability_type' => 'post'
    ));
});

add_action('add_meta_boxes_mng_gear', function () {
    add_meta_box('mng_gear_meta', '週間おすすめの評価と商品リンク', 'mng_gear_meta_box', 'mng_gear', 'normal', 'high');
});
function mng_gear_fields() {
    return array(
        'article_id' => '深掘り記事の投稿ID（公開済みの投稿のみ）',
        'pochipp_id' => 'Pochippの商品管理ID（正式成果リンクを確認済みの場合のみ）',
        'newness' => '新製品・ニュースの鮮度 0–100',
        'trend' => 'SNS・検索需要の注目度 0–100',
        'demand' => '読者の購入意欲・検索意図 0–100',
        'revenue' => 'ASP成果の評価 0–100（実績不明なら0）',
        'editor' => '編集部おすすめ度 0–100',
        'verified' => '報酬リンク検証済み 1＝はい / 0＝いいえ',
        'ready' => '掲載準備完了 1＝はい / 0＝いいえ',
        'release_note' => '発売情報・時期（例：2026年12月12日発売予定）',
        'reason' => '今週注目する理由（短く、出典を確認）',
        'official_url' => 'メーカー公式URL（httpsのみ）'
    );
}
function mng_gear_meta_box($post) {
    wp_nonce_field('mng_gear_save', 'mng_gear_nonce');
    foreach (mng_gear_fields() as $key => $label) {
        $v = get_post_meta($post->ID, '_mng_' . $key, true);
        echo '<p><label for="mng_' . esc_attr($key) . '"><strong>' . esc_html($label) . '</strong></label>';
        echo '<input style="display:block;width:100%" id="mng_' . esc_attr($key) . '" name="mng_' . esc_attr($key) . '" value="' . esc_attr($v) . '"></p>';
    }
    echo '<p>掲載基準：準備完了・公開済み深掘り記事を必須とします。Pochipp広告は報酬リンク検証済みだけ表示。売上実績が不明なら0点。</p>';
}
add_action('save_post_mng_gear', function ($post_id) {
    if (!isset($_POST['mng_gear_nonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['mng_gear_nonce'])), 'mng_gear_save')) return;
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
    if (!current_user_can('edit_post', $post_id)) return;
    foreach (array_keys(mng_gear_fields()) as $key) {
        if (!isset($_POST['mng_' . $key])) continue;
        $raw = wp_unslash($_POST['mng_' . $key]);
        if (in_array($key, array('article_id','pochipp_id','newness','trend','demand','revenue','editor','verified','ready'), true)) {
            $value = absint($raw);
            if (in_array($key, array('newness','trend','demand','revenue','editor'), true)) $value = min(100,$value);
            if (in_array($key, array('verified','ready'), true)) $value = min(1,$value);
        } elseif ($key === 'official_url') {
            $value = esc_url_raw($raw, array('https'));
        } else $value = sanitize_text_field($raw);
        update_post_meta($post_id, '_mng_' . $key, $value);
    }
});
function mng_pick_score($id, $week) {
    $w = array('newness'=>30,'trend'=>25,'demand'=>20,'revenue'=>15,'editor'=>10);
    $score = 0;
    foreach ($w as $k=>$weight) $score += min(100, absint(get_post_meta($id,'_mng_'.$k,true))) * $weight / 100;
    // Stable tie-break for each ISO week. Randomness never outweighs data by >3 points.
    $hash = hexdec(substr(md5($week . ':' . $id),0,4)) / 65535;
    return $score + $hash * 3;
}
add_shortcode('mng_weekly_gear', function ($atts) {
    $atts = shortcode_atts(array('count'=>3), $atts, 'mng_weekly_gear');
    $count = max(1,min(6,absint($atts['count'])));
    // WP timezone rather than server timezone, Japanese ISO week. Can rotate without daily jobs.
    $now = current_datetime();
    $week = $now->format('o-W');
    $items = get_posts(array('post_type'=>'mng_gear','post_status'=>'publish','numberposts'=>200,'orderby'=>'ID','order'=>'DESC'));
    $ranked = array();
    foreach ($items as $item) {
        $id=$item->ID;
        if ((int)get_post_meta($id,'_mng_ready',true)!==1) continue;
        $article_id=absint(get_post_meta($id,'_mng_article_id',true));
        if (!$article_id || get_post_status($article_id)!=='publish' || get_post_type($article_id)!=='post') continue;
        $ranked[]=array('id'=>$id,'article_id'=>$article_id,'score'=>mng_pick_score($id,$week));
    }
    usort($ranked, function($a,$b){$v=$b['score']<=>$a['score'];return $v!==0?$v:($a['id']<=>$b['id']);});
    $ranked=array_slice($ranked,0,$count);
    if (!$ranked) return '<p class="mng-week-empty">今週の注目機材は準備中です。記事一覧から機材を探せます。</p>';
    $out='<section class="mng-week" aria-labelledby="mng-week-title"><div class="mng-week-head"><div><p class="mng-week-kicker">WEEKLY GEAR PICKS</p><h2 id="mng-week-title">今週の注目機材</h2></div><span class="mng-week-period">'.esc_html($now->format('Y').'年 第'.$now->format('W').'週').'</span></div>';
    $out.='<p class="mng-week-desc">新製品・トレンド・購入ニーズ・確認できた成果をもとに、編集部が今週の候補を選定しています。売上ランキングではありません。</p><div class="mng-week-grid">';
    foreach($ranked as $row) {
        $id=$row['id'];$article=$row['article_id'];
        $name=get_the_title($id);$url=get_permalink($article);
        $note=get_post_meta($id,'_mng_reason',true);
        $release=get_post_meta($id,'_mng_release_note',true);
        $pid=absint(get_post_meta($id,'_mng_pochipp_id',true));
        $verified=(int)get_post_meta($id,'_mng_verified',true)===1;
        $photo=get_the_post_thumbnail($id,'medium_large',array('loading'=>'lazy','alt'=>$name));
        $out.='<article class="mng-week-card"><a class="mng-week-product" href="'.esc_url($url).'"><div class="mng-week-photo">'.($photo ? $photo : '<span class="mng-week-noimage">MY NEW GEAR</span>').'</div><div class="mng-week-copy">';
        if ($release) $out.='<span class="mng-week-label">'.esc_html($release).'</span>';
        $out.='<h3>'.esc_html($name).'</h3>';
        if ($note) $out.='<p>'.esc_html($note).'</p>';
        $out.='<strong class="mng-week-link">詳しい比較・解説を見る</strong></div></a>';
        // Render a real Pochipp card only after a human has verified the merchant links.
        if ($verified && $pid && shortcode_exists('pochipp')) {
            $shortcode='[pochipp id="'.$pid.'"]';
            $out.='<div class="mng-week-affiliate">'.do_shortcode($shortcode).'</div>';
        }
        $out.='</article>';
    }
    return $out.'</div><p class="mng-week-disclosure">PR：一部の商品紹介には広告が含まれます。掲載順は売上額の順位ではありません。</p></section>';
});
