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
				<p>Each response is mapped below, with data clustered into groups. Click the clusters to reveal the single data points. Single data points can be clicked to view the logged data.</p>
				<p>The location points shown have a random distance added, within 500m, to preserve our participants privacy.</p>
				<div id='bb-mapid'>
					<div id='bb-loader'>
						<span id='bb-loader-text'>Loading data...</span><br>
						<span id='bb-loader-count'>0</span> points
					</div>
				</div>
				<!--
				<h3>Data summaries</h3>
				<p>A summary of the data collected is shown in the charts below. </p>
				<div id='bb-charts'>
					<div id='bb-gender-chart-wrapper'>
						<canvas id='bb-gender-chart' width='400' height='400'></canvas>
						<div id='bb-gender-legend' class='chart-legend'></div>
					</div>
	
	
					<div id='bb-age-chart-wrapper'>
						<canvas id='bb-age-chart' width='400' height='400'></canvas>
						<div id='bb-age-legend' class='chart-legend'></div>
					</div>
					<div class='clear'></div>
				</div>
				-->
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
			wp_enqueue_style('markercluster_css', plugins_url('css/markercluster.css', __FILE__));
			wp_enqueue_style('markerclusterd_css', plugins_url('css/markercluster-default.css', __FILE__));
			wp_enqueue_style('bbmap_css', plugins_url('css/bb-map.css', __FILE__));
			//wp_enqueue_style('bbchart_css', plugins_url('css/bb-chart.css', __FILE__));
			
			wp_enqueue_script('jquery_js', plugins_url('js/jquery.js', __FILE__));
			//wp_enqueue_script('chart_js', 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.1.3/Chart.min.js');
			wp_enqueue_script('leaflet_js', 'http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js');
			wp_enqueue_script('markercluster_js', plugins_url('js/markercluster.js', __FILE__));
			wp_enqueue_script('bbmap_js', plugins_url('js/bb-map.js' ,__FILE__));
			//wp_enqueue_script('bbchart_js', plugins_url('js/bb-chart.js' ,__FILE__));
			//wp_enqueue_script('bbchartgender_js', plugins_url('js/bb-gender-data.js' ,__FILE__));
			//wp_enqueue_script('bbchartage_js', plugins_url('js/bb-age-data.js' ,__FILE__));
		}
	}
}

$bbdataviz = new BBDataViz();
