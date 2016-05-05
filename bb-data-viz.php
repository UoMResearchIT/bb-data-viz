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
		add_shortcode('bb-data-viz', array($this, 'holdingMapImage'));
		
	}
	
	public function holdingMapImage() {
		// Display the holding page map
		echo '<p>We\'re currently busy collecting data for Britain Breathing. Please check back for updates soon.</p>';
		
		echo '<p><img src="'.plugins_url('imgs/bb_map.jpg', __FILE__ ).'" alt="Map data coming soon..." style="width:100%"></p>';
	}
	
	public function loadMap() {
		// Get JSON from the API
		
		// Parse onto the map
		
		// Add map to the page
		
	}
}

$bbdataviz = new BBDataViz();
