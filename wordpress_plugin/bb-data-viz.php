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
		//add_action('wp_head', $this->leafletFiles());
	}
	
	public function holdingMapImage() {
		// Display the holding page map
		echo '<p>We\'re currently busy collecting data for Britain Breathing. Please check back for updates soon.</p>';
		
		echo '<p><img src="'.plugins_url('imgs/bb_map.jpg', __FILE__ ).'" alt="Map data coming soon..." style="width:100%"></p>';
	}
	
	public function loadMap() {
		// Add the map div
		//echo '<div id="bb-mapid"></div>';
		readfile(plugins_url('dataviz.html', __FILE__ ));
		
		// All the parsing et cetera is done in the js files client side...
	}
	
	public function leafletFiles() {
		if (!is_admin()) {
			/*
			$leaflet = '
			<link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.css" />
			<link rel="stylesheet" href="'.plugins_url('css/bb-map.css', __FILE__ ).'" />
			<script src="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js"></script>
			<script src="'.plugins_url('js/bb-map.js', __FILE__ ).'"></script>';
			
			echo $leaflet;
			
			wp_enqueue_script('leaflet_css', 'http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.css');
			wp_enqueue_script('bb_css', plugins_url('css/bb-map.css', __FILE__));
			wp_enqueue_script('leaflet_js', 'http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js');
			wp_enqueue_script('bb_js', plugins_url('js/bb-map.js' ,__FILE__));
			*/
		}
	}
}

$bbdataviz = new BBDataViz();
