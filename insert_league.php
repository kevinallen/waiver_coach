<?php
include 'couchhelper.php';
include 'yahoo_api.php';

$options['host'] = "localhost";
$options['port'] = 5984;

$couch = new CouchHelper($options); // See if we can make a connection
$resp = $couch->send("GET", "/");

// insert data
// TODO: parameterize API url
$url = 'http://fantasysports.yahooapis.com/fantasy/v2/league/348.l.511174/'
     . 'teams?format=json';
$data = oauth_request($url); // function in yahoo_api.php
$json = json_decode($data, true);
$league_key = $json['fantasy_content']['league'][0]['league_key'];
$resp = $couch->send("PUT","/leagues/$league_key",json_encode($json));
echo $resp;
?>
