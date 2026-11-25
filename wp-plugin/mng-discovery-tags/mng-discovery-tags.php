<?php
/**
 * Plugin Name: MyNewGear Discovery Tags
 * Description: Routes sound / budget chips to populated WordPress tag archives only.
 * Version: 0.1.0
 */
defined('ABSPATH') || exit;
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('mng-discovery', plugins_url('style.css', __FILE__), array(), '0.1.0');
});
add_shortcode('mng_discovery', function ($atts) {
    $atts=shortcode_atts(array('mode'=>'sound'),$atts,'mng_discovery');
    $items=array(
      'sound'=>array(
        array('label'=>'軽い歪み','slug'=>'sound-light-drive'),
        array('label'=>'迫力のある歪み','slug'=>'sound-heavy-drive'),
        array('label'=>'ファズ','slug'=>'sound-fuzz'),
        array('label'=>'ディレイ・残響','slug'=>'sound-delay-reverb'),
        array('label'=>'マルチエフェクター','slug'=>'sound-multi-effects')
      ),
      'budget'=>array(
        array('label'=>'1万円前後','slug'=>'budget-around-10000'),
        array('label'=>'3万円前後','slug'=>'budget-around-30000'),
        array('label'=>'5万円前後','slug'=>'budget-around-50000')
      )
    );
    $mode=sanitize_key($atts['mode']);
    if (!isset($items[$mode])) return '';
    $out='<nav class="mng-discovery-tags" aria-label="'.esc_attr($mode==='sound'?'欲しい音から探す':'予算から探す').'">';
    foreach($items[$mode] as $item) {
        $tag=get_term_by('slug',$item['slug'],'post_tag');
        if ($tag && !is_wp_error($tag) && (int)$tag->count>0) {
            $link=get_term_link($tag);
            if (!is_wp_error($link)) {
                $out.='<a class="mng-discovery-chip" href="'.esc_url($link).'">'.esc_html($item['label']).'</a>';
                continue;
            }
        }
        // Never send users to empty search results or # placeholder.
        $out.='<span class="mng-discovery-chip is-pending" aria-label="'.esc_attr($item['label'].'、記事準備中').'"><span>'.esc_html($item['label']).'</span><small>準備中</small></span>';
    }
    return $out.'</nav>';
});
