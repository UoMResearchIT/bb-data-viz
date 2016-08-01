<?php defined('ABSPATH') or die('No direct access, sorry about that.');
/**
 * Britain Breathing Data Visualisation Plugin
 *
 * @package     BritainBreathing
 * @author      Rob Dunne
 * @copyright   2016 University of Manchester
 * @license     GPL-2.0+
 *
 * @wordpress-plugin
 * Plugin Name:  Britain Breathing Data Visualisation
 * Plugin URI:  https://manchester.ac.uk
 * Description: Plot research data to a map.
 * Version:     1.0.0
 * Author:      Rob Dunne
 * Author URI:  https://manchester.ac.uk
 * Text Domain: bb-data-viz
 * License:     GPL-2.0+
 * License URI: http://www.gnu.org/licenses/gpl-2.0.txt
 */

class BBDataViz {
	public function __construct() {
		// Add the plugin shortcode
		add_shortcode('bb-data-viz', array($this, 'loadMap'));
		
		// Add the files to the page header
		if (strpos($_SERVER['REQUEST_URI'], 'data-visualisation') !== false){
			add_action('wp_head', $this->leafletFiles());
		}
	}
	
	public function holdingMapImage() {
		// Display the holding page map
		echo '<p>We\'re currently busy collecting data for Britain Breathing. Please check back for updates soon.</p>';
		
		echo '<p><img src="'.plugins_url('imgs/bb_map.jpg', __FILE__ ).'" alt="Map data coming soon..." style="width:100%"></p>';
	}
	
	public function loadMap() {
		// Add the map div
		echo '
			<div id="bb-loader">
				<img src="'.plugins_url('imgs/loading.svg', __FILE__).'" alt="">
				<div id="bb-loader-text"></div>
			</div>

			<div id="bb-filters">
				<div id="bb-options">
					<span class="bb-map-control bb-map-control-active" id="bb-map-overview" data-kml-file="symptom_score.kml" data-timeline="all">All symptoms</span>
					<span class="bb-map-control" id="bb-map-feeling" data-kml-file="how_feeling_score.kml" data-timeline="feeling">How feeling symptoms</span>
					<span class="bb-map-control" id="bb-map-nose" data-kml-file="nose_score.kml" data-timeline="nose">Nose symptoms</span>
					<span class="bb-map-control" id="bb-map-eyes" data-kml-file="eyes_score.kml" data-timeline="eyes">Eyes symptoms</span>
					<span class="bb-map-control" id="bb-map-breathing" data-kml-file="breathing_score.kml" data-timeline="breathing">Breathing symptoms</span>
				</div>
	
				<div id="bb-timeline">
					Weekly data timeline: <span id="bb-start-date"></span> to <span id="bb-end-date"></span>
				</div>
	
				<div id="bb-slider"></div>
			</div>

			<div id="bb-mapid"></div>

			<div id="bb-map-legend">
				<h4>Symptom scores:</h4>
				<span class="bb-map-key"><span id="bb-map-key-none"></span> No data</span>
				<span class="bb-map-key"><span id="bb-map-key-green"></span> 0: No symptoms</span>
				<span class="bb-map-key"><span id="bb-map-key-yellow"></span> 1: Moderate</span>
				<span class="bb-map-key"><span id="bb-map-key-red"></span> 2: Severe</span>
			</div>';
			
		// All the data parsing etc is done in the js files client side...
	}
	
	public function leafletFiles() {
		if (!is_admin()) {
			wp_deregister_script('jquery');
			wp_register_script('jquery', ("http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js"), false, '1.3.2');
			wp_enqueue_script('jquery');
			
			// Add the header files
			wp_enqueue_style('slider_css', 'https://code.jquery.com/ui/1.12.0/themes/south-street/jquery-ui.css');
			wp_enqueue_style('bbmap_css', plugins_url('css/bb-map.css', __FILE__));
			wp_enqueue_style('pips_css', plugins_url('css/jquery-ui-slider-pips.css', __FILE__));
			
			wp_enqueue_script('jquery_js', plugins_url('js/jquery.js', __FILE__));
			wp_enqueue_script('jqui_js', 'https://code.jquery.com/ui/1.12.0/jquery-ui.js');
			wp_enqueue_script('date_js', plugins_url('js/date.js' ,__FILE__));
			wp_enqueue_script('pips_js', plugins_url('js/jquery-ui-slider-pips.js' ,__FILE__));
			wp_enqueue_script('bbmap_js', plugins_url('js/bb-map.js' ,__FILE__));
			wp_enqueue_script('gmaps_js', 'https://maps.googleapis.com/maps/api/js?key=AIzaSyBSn93izC-nPH7tSk1_-BK6D59whEpWFQo&callback=initMapData');
		}
	}
}

$bbdataviz = new BBDataViz();
