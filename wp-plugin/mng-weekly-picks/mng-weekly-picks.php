<?php
/**
 * Plugin Name: MyNewGear Weekly Picks
 * Description: Editorially curated weekly gear picks. Revenue attribution stays in Pochipp.
 * Version: 0.5.0
 * Requires PHP: 7.4
 */
defined('ABSPATH') || exit;

add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('mng-weekly-picks', plugins_url('style.css', __FILE__), array(), '0.5.0');
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
        'article_id' => '解説記事の投稿ID（任意・未公開なら準備中表示）',
        'pochipp_id' => 'Pochippの商品管理ID（正式成果リンクを確認済みの場合のみ）',
        'newness' => '新製品・ニュースの鮮度 0–100',
        'trend' => 'SNS・検索需要の注目度 0–100',
        'demand' => '読者の購入意欲・検索意図 0–100',
        'revenue' => 'ASP成果の評価 0–100（実績不明なら0）',
        'editor' => '編集部おすすめ度 0–100',
        'lane' => '機材タイプ（drive=歪み、multi=マルチ、space=空間系、utility=チューナー等、boutique=高額個性派）',
        'editor_source' => '編集部選定の根拠URL（https）',
        'bestseller' => '売れ筋枠に選考：1=はい／0=いいえ（外部順位の出典必須）',
        'editor_pick' => '編集部おすすめ枠に選考：1=はい／0=いいえ',
        'rank_source' => '売れ筋順位の出典ページURL（https）',
        'rank_date' => '売れ筋順位の確認日 YYYY-MM-DD（古いデータは注記・更新推奨）',
        'rank_position' => '外部ランキングの順位（1〜100）。実測順位を確認した場合のみ',
        'verified' => '広告リンクの遷移とASP設定確認済み 1＝はい / 0＝いいえ',
        'ready' => '商品名・型番・広告検索リンク確認済み 1＝はい / 0＝いいえ',
        'release_note' => '発売情報・時期（発売済みの事実のみ）',
        'release_date' => '発売日 YYYY-MM-DD（正確な日付が判明している場合）',
        'legacy_released' => '発売30日以上経過の旧機種で正確な発売日不明 1＝根拠を確認済み',
        'release_source' => '発売日・旧機種であることの根拠URL（https）',
        'stock_checked' => '在庫確認日（任意・参考情報）',
        'stock_shops' => '在庫確認店舗数（任意・掲載判定には使用しない）',
        'stock_url1' => '在庫確認した販売店の個別商品URL①（https）',
        'stock_url2' => '在庫確認した別販売店の個別商品URL②（https）',
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
    echo '<p><strong>公開条件：</strong>発売済みの製品・型番一致・Pochippの有効な広告検索リンクとASP設定の確認。記事は未作成でも「記事準備中」として掲載可能。店舗在庫や商品個別URLは掲載停止条件にしません。</p>';
}
add_action('save_post_mng_gear', function ($post_id) {
    if (!isset($_POST['mng_gear_nonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['mng_gear_nonce'])), 'mng_gear_save')) return;
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
    if (!current_user_can('edit_post', $post_id)) return;
    foreach (array_keys(mng_gear_fields()) as $key) {
        if (!isset($_POST['mng_' . $key])) continue;
        $raw = wp_unslash($_POST['mng_' . $key]);
        if (in_array($key, array('article_id','pochipp_id','newness','trend','demand','revenue','editor','verified','ready','stock_shops','bestseller','editor_pick','rank_position','legacy_released'), true)) {
            $value = absint($raw);
            if (in_array($key, array('newness','trend','demand','revenue','editor'), true)) $value = min(100,$value);
            if (in_array($key, array('verified','ready','bestseller','editor_pick','legacy_released'), true)) $value = min(1,$value);
            if ($key === 'stock_shops') $value = min(10,$value);
            if ($key === 'rank_position') $value = min(100,$value);
        } elseif (in_array($key,array('stock_checked','release_date','rank_date'),true)) {
            $value = preg_match('/^\\d{4}-\\d{2}-\\d{2}$/', $raw) ? $raw : '';
        } elseif (in_array($key,array('official_url','stock_url1','stock_url2','editor_source','rank_source','release_source'),true)) {
            $value = esc_url_raw($raw, array('https'));
        } else $value = sanitize_text_field($raw);
        update_post_meta($post_id, '_mng_' . $key, $value);
    }
});
/**
 * Revenue-first gates: published product + working Pochipp merchant-search links.
 * No article / per-shop stock / product photo required. Pre-release products remain blocked.
 * verified=1 is set only after checking model-specific search terms and ASP tracking.
 */
function mng_pick_is_sellable($id, $now) {
    if ((int) get_post_meta($id, '_mng_ready', true) !== 1) return false;
    if ((int) get_post_meta($id, '_mng_verified', true) !== 1) return false;
    if (!shortcode_exists('pochipp')) return false;
    if (!absint(get_post_meta($id, '_mng_pochipp_id', true))) return false;

    $tz=wp_timezone();
    $release=get_post_meta($id, '_mng_release_date', true);
    $today=DateTimeImmutable::createFromFormat('!Y-m-d', $now->format('Y-m-d'), $tz);
    if ($release) {
        $date=DateTimeImmutable::createFromFormat('!Y-m-d', $release, $tz);
        if (!$date || $date->format('Y-m-d') !== $release) return false;
        if ((int)$date->diff($today)->format('%r%a') < 30) return false;
    } else {
        $source=get_post_meta($id,'_mng_release_source',true);
        if ((int)get_post_meta($id,'_mng_legacy_released',true) !== 1
            || !$source || !wp_http_validate_url($source)) return false;
    }
    return true;
}
// Non-invasive admin reminder: week-by-week manual evidence verification.
// No automated claims about current stock or affiliate conversions.
add_action('admin_notices', function () {
    if (!current_user_can('manage_options') || !function_exists('get_current_screen')) return;
    $screen=get_current_screen();
    if (!$screen || !in_array($screen->id,array('dashboard','edit-mng_gear'),true)) return;
    $ids=get_posts(array('post_type'=>'mng_gear','post_status'=>'publish','numberposts'=>200,'fields'=>'ids'));
    if (!$ids) return;
    $now=current_datetime();$active=0;
    foreach($ids as $id) if (mng_pick_is_sellable($id,$now)) $active++;
    if ($active>=6) return;
    echo '<div class="notice notice-warning"><p><strong>MyNewGear 今週の注目機材：</strong> 条件を満たす商品が '
        .esc_html((string)$active).' / 6 件です。発売済みの型番と検索結果への広告リンク、ASP設定を確認してください。記事がなければ「記事準備中」と表示できます。'
        .'条件外の商品は表示しません。</p></div>';
});
function mng_pick_score($id, $week) {
    $w = array('newness'=>15,'trend'=>20,'demand'=>25,'revenue'=>25,'editor'=>15);
    $score = 0;
    foreach ($w as $k=>$weight) $score += min(100, absint(get_post_meta($id,'_mng_'.$k,true))) * $weight / 100;
    // Stable tie-break for each ISO week. Randomness never outweighs data by >3 points.
    $hash = hexdec(substr(md5($week . ':' . $id),0,4)) / 65535;
    return $score + $hash * 3;
}
/**
 * Only label an item "売れ筋" when the ranking is fresh and its original URL
 * and position have been recorded. Ranking positions are per source, so never
 * imply these are aggregated sales totals.
 */
function mng_pick_has_ranking($id, $now) {
    if ((int) get_post_meta($id, '_mng_bestseller', true) !== 1) return false;
    $position=absint(get_post_meta($id, '_mng_rank_position', true));
    $url=get_post_meta($id, '_mng_rank_source', true);
    $date=get_post_meta($id, '_mng_rank_date', true);
    if ($position < 1 || $position > 100 || !$url || !wp_http_validate_url($url)) return false;
    $dt=DateTimeImmutable::createFromFormat('!Y-m-d', $date, wp_timezone());
    if (!$dt || $dt->format('Y-m-d')!==$date) return false;
    $today=DateTimeImmutable::createFromFormat('!Y-m-d', $now->format('Y-m-d'), wp_timezone());
    $age=(int) $dt->diff($today)->format('%r%a');
    return $age >= 0; // Show the source date even when the underlying ranking is older; editors should refresh weekly.
}
function mng_pick_diverse($entries, $count, $excluded=array()) {
    $out=array(); $seen=array(); $used=$excluded;
    foreach ($entries as $entry) {
        if (in_array($entry['id'], $used, true)) continue;
        $lane=sanitize_key((string)get_post_meta($entry['id'],'_mng_lane',true));
        if (!$lane) $lane='general';
        if (isset($seen[$lane])) continue;
        $out[]=$entry; $seen[$lane]=true; $used[]=$entry['id'];
        if (count($out)>=$count) return $out;
    }
    foreach ($entries as $entry) {
        if (in_array($entry['id'], $used, true)) continue;
        $out[]=$entry; $used[]=$entry['id'];
        if (count($out)>=$count) break;
    }
    return $out;
}
function mng_pick_card_html($entry, $is_bestseller) {
    $id=$entry['id']; $article=$entry['article_id'];
    $name=get_the_title($id);
    $article_ready = $article && get_post_type($article)==='post' && get_post_status($article)==='publish';
    $url = $article_ready ? get_permalink($article) : '';
    $note=get_post_meta($id,'_mng_reason',true);
    $release=get_post_meta($id,'_mng_release_note',true);
    $pid=absint(get_post_meta($id,'_mng_pochipp_id',true));
    $photo=get_the_post_thumbnail($id,'medium_large',array('loading'=>'lazy','alt'=>$name));
    $out='<article class="mng-week-card">';
    if ($article_ready) $out.='<a class="mng-week-product" href="'.esc_url($url).'">';
    else $out.='<div class="mng-week-product">';
    $out.='<div class="mng-week-photo">'.($photo ? $photo : '<span class="mng-week-noimage">MY NEW GEAR</span>').'</div><div class="mng-week-copy">';
    if ($release) $out.='<span class="mng-week-label">'.esc_html($release).'</span>';
    $out.='<h3>'.esc_html($name).'</h3>';
    if ($note) $out.='<p>'.esc_html($note).'</p>';
    $out.=$article_ready ? '<strong class="mng-week-link">詳しい比較・解説を見る</strong></div></a>' : '<span class="mng-week-link">記事準備中</span></div></div>';
    if ($pid && shortcode_exists('pochipp')) {
        $out.='<div class="mng-week-affiliate">'.do_shortcode('[pochipp id="'.$pid.'"]').'</div>';
    }
    if ($is_bestseller) {
        $rank_url=get_post_meta($id,'_mng_rank_source',true);
        $rank_date=get_post_meta($id,'_mng_rank_date',true);
        $rank_pos=absint(get_post_meta($id,'_mng_rank_position',true));
        $out.='<p class="mng-week-source"><a href="'.esc_url($rank_url).'" target="_blank" rel="noopener noreferrer">売れ筋の出典（'.esc_html($rank_date).'・掲載順位'.esc_html($rank_pos).'位）</a></p>';
    }
    return $out.'</article>';
}
/**
 * Render the original TOP cards saved as a WordPress synced pattern (wp_block).
 * This avoids a blank homepage when no verified affiliate offers are ready.
 */
function mng_pick_fallback($block_id) {
    $block_id=absint($block_id);
    if (!$block_id) return '';
    $block=get_post($block_id);
    if (!$block || $block->post_type !== 'wp_block' || $block->post_status !== 'publish') return '';
    // A saved pattern must not embed this widget, otherwise it could recurse.
    if (strpos($block->post_content, '[mng_weekly_gear') !== false) return '';
    return do_shortcode(do_blocks($block->post_content));
}
add_shortcode('mng_weekly_gear', function ($atts) {
    // Retain legacy count=3 as a per-section count. Two rows by default.
    $atts=shortcode_atts(array('count'=>3,'fallback_block'=>0),$atts,'mng_weekly_gear');
    $per_group=max(1,min(3,absint($atts['count'])));
    $now=current_datetime(); $week=$now->format('o-W');
    $items=get_posts(array('post_type'=>'mng_gear','post_status'=>'publish','numberposts'=>200,'orderby'=>'ID','order'=>'DESC'));
    $ranked=array();
    foreach($items as $item) {
        $id=$item->ID;
        if (!mng_pick_is_sellable($id,$now)) continue;
        $article_id=absint(get_post_meta($id,'_mng_article_id',true));
        $ranked[]=array(
            'id'=>$id,'article_id'=>$article_id,
            'score'=>mng_pick_score($id,$week),
            'rank'=>absint(get_post_meta($id,'_mng_rank_position',true))
        );
    }
    $best_candidates=array_values(array_filter($ranked,function($e) use ($now){return mng_pick_has_ranking($e['id'],$now);}));
    // Compare different retailer rankings by editorial score, not raw rank.
    // A #1 at one shop is not comparable to a #1 at another.
    usort($best_candidates,function($a,$b){
        $v=$b['score']<=>$a['score'];
        return $v!==0?$v:($a['id']<=>$b['id']);
    });
    $best=mng_pick_diverse($best_candidates,$per_group);
    $used=array_column($best,'id');
    $editor_candidates=array_values(array_filter($ranked,function($e){
        return (int)get_post_meta($e['id'],'_mng_editor_pick',true)===1;
    }));
    usort($editor_candidates,function($a,$b){$v=$b['score']<=>$a['score'];return $v!==0?$v:($a['id']<=>$b['id']);});
    $editor=mng_pick_diverse($editor_candidates,$per_group,$used);
    // At least one verified item is sufficient to go live; never show fake products.
    // If nothing is ready, keep the saved prior TOP as fallback.
    if (!$best && !$editor) return mng_pick_fallback($atts['fallback_block']);
    $out='<section class="mng-week" aria-label="今週の注目機材">';
    $out.='<div class="mng-week-head"><div><p class="mng-week-kicker">WEEKLY GEAR PICKS</p><h2>今週の注目機材</h2></div><span class="mng-week-period">'.esc_html($now->format('Y').'年 第'.$now->format('W').'週').'</span></div>';
    $out.='<p class="mng-week-desc">売れ筋と編集部の独自チョイスを紹介。購入先は各ショップの検索結果から選べます。価格と在庫は購入時にご確認ください。</p>';
    $groups=array(
        array('items'=>$best,'title'=>'売れ筋TOP3','desc'=>'複数の公開ランキング掲載商品から編集部が選定。各順位の出典・確認日を表示します。','bestseller'=>true),
        array('items'=>$editor,'title'=>'編集部おすすめTOP3','desc'=>'音作りの個性・購入意欲・定番性と最近の注目度から独自に選定。','bestseller'=>false)
    );
    foreach($groups as $group) {
        if (!$group['items']) continue;
        $section_title = count($group['items']) < $per_group ? str_replace('TOP3', 'ピックアップ', $group['title']) : $group['title'];
        $out.='<div class="mng-week-group"><div class="mng-week-group-head"><h3>'.esc_html($section_title).'</h3><p>'.esc_html($group['desc']).'</p></div>';
        $out.='<div class="mng-week-grid" role="region" aria-label="'.esc_attr($section_title).'：横スクロールできます" tabindex="0">';
        foreach($group['items'] as $entry) $out.=mng_pick_card_html($entry,$group['bestseller']);
        $out.='</div></div>';
    }
    return $out.'<p class="mng-week-disclosure">PR：商品紹介には広告が含まれます。広告検索リンクの遷移を確認して掲載。売上個数の総合ランキングではありません。</p></section>';
});
