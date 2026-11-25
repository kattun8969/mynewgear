<?php
/**
 * Run with: wp eval-file wp-plugin/mng-weekly-picks/seed-weekly-gear.php
 * Preconditions: WordPress CLI and the MyNewGear Weekly Picks plugin enabled.
 * Safe idempotent seed. It NEVER enables product publication or verified affiliate flags.
 */
if (!defined('ABSPATH')) exit(1);
if (!post_type_exists('mng_gear')) { WP_CLI::error('Activate the weekly picks plugin first.'); }
$products = array(
  array('title'=>'ZOOM MS-70CDR+', 'lane'=>'space', 'bestseller'=>1, 'editor_pick'=>0, 'newness'=>25, 'trend'=>85, 'demand'=>90, 'editor'=>92, 'rank_position'=>1, 'rank_source'=>'https://kakaku.com/gakki/effector/ranking_2803/spec%3D101-1/', 'rank_date'=>'2026-11-24', 'reason'=>'空間系の幅広い音作りを手軽に追加'),
  array('title'=>'BOSS GX-1', 'lane'=>'multi', 'bestseller'=>1, 'editor_pick'=>0, 'newness'=>70, 'trend'=>95, 'demand'=>92, 'editor'=>90, 'rank_position'=>2, 'rank_source'=>'https://kakaku.com/gakki/effector/ranking_2803/spec%3D101-1/', 'rank_date'=>'2026-11-24', 'reason'=>'2026年発売のコンパクトなマルチ'),
  array('title'=>'BOSS BD-2 Blues Driver', 'lane'=>'drive', 'bestseller'=>1, 'editor_pick'=>0, 'newness'=>0, 'trend'=>85, 'demand'=>96, 'editor'=>92, 'rank_position'=>8, 'rank_source'=>'https://www.soundhouse.co.jp/bestseller/middle/142/', 'rank_date'=>'2026-11-25', 'reason'=>'定番ブルースドライバーを比較'),
  array('title'=>'VEMURAM Jan Ray', 'lane'=>'boutique', 'bestseller'=>0, 'editor_pick'=>1, 'newness'=>5, 'trend'=>82, 'demand'=>58, 'editor'=>92, 'reason'=>'高価格帯のアンプライクな歪みを比較'),
  array('title'=>'TC Electronic PolyTune 3', 'lane'=>'utility', 'bestseller'=>0, 'editor_pick'=>1, 'newness'=>10, 'trend'=>84, 'demand'=>92, 'editor'=>90, 'reason'=>'実用性の高いペダル型チューナー'),
  array('title'=>'ZOOM MS-50G+', 'lane'=>'multi', 'bestseller'=>0, 'editor_pick'=>1, 'newness'=>20, 'trend'=>75, 'demand'=>82, 'editor'=>85, 'reason'=>'コンパクトなマルチストンプを比較'),
);
foreach($products as $p) {
    $existing=get_posts(array('post_type'=>'mng_gear','post_status'=>'any','numberposts'=>-1,'fields'=>'ids','suppress_filters'=>true));
    $id=0;
    foreach($existing as $candidate) {
       if (get_the_title($candidate)===$p['title']) { $id=$candidate; break; }
    }
    if (!$id) {
        $id=wp_insert_post(array('post_type'=>'mng_gear','post_status'=>'publish','post_title'=>$p['title']),true);
        if (is_wp_error($id)) { WP_CLI::warning($p['title'].' skipped: '.$id->get_error_message());continue; }
    }
    foreach($p as $key=>$value) {
        if($key==='title')continue;
        // Do not replace an operator's newer editorial scores or changed URLs.
        if (get_post_meta($id,'_mng_'.$key,true)==='') update_post_meta($id,'_mng_'.$key,$value);
    }
    // No affiliate identity or real product permalink has been verified here.
    // A user could have already verified one; preserve such settings.
    if (get_post_meta($id,'_mng_ready',true)==='') update_post_meta($id,'_mng_ready',0);
    if (get_post_meta($id,'_mng_verified',true)==='') update_post_meta($id,'_mng_verified',0);
    if (get_post_meta($id,'_mng_revenue',true)==='') update_post_meta($id,'_mng_revenue',0);
    WP_CLI::log('Created/updated candidate: '.$p['title'].' (ID '.$id.')');
}
WP_CLI::success('Six candidates created. The TOP remains unchanged until each product affiliate link is verified.');
