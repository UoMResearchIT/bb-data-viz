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
		echo "
			<div id='bb-data-viz-wrapper'>
				<h3>Mapping the data points</h3>
				<p>The Britain Breathing data is aggregated and mapped according to UK postcode.</p>
				<p>The location points shown have a random distance added, within 500m, to preserve our participants privacy.</p>
				<div id='bb-mapid'>
					<div id='bb-loader'>
						<span id='bb-loader-text'>Loading data...</span><br>
						<span id='bb-loader-count'>0</span> points
					</div>
				</div>
			</div>";
			
		// All the data parsing etc is done in the js files client side...
	}
	
	public function leafletFiles() {
		if (!is_admin()) {
			wp_deregister_script('jquery');
			wp_register_script('jquery', ("http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js"), false, '1.3.2');
			wp_enqueue_script('jquery');
			
			// Add the header files
			wp_enqueue_style('leaflet_css', plugins_url('css/leaflet.css', __FILE__));
			wp_enqueue_style('bbmap_css', plugins_url('css/bb-map.css', __FILE__));
			
			wp_enqueue_script('jquery_js', plugins_url('js/jquery.js', __FILE__));
			wp_enqueue_script('leaflet_js', 'http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js');
			wp_enqueue_script('bbmap_js', plugins_url('js/bb-map.js' ,__FILE__));
		}
	}
}

$bbdataviz = new BBDataViz();
