<?php
include 'couchhelper.php';
include 'yahoo_api.php';

$options['host'] = "localhost";
$options['port'] = 5984;

$couch = new CouchHelper($options); // See if we can make a connection

// read league data
// TODO: lookup league_key
$resp = $couch->send("GET", "/leagues/348.l.511174");
$league = json_decode($resp, true);
$num_teams = $league['fantasy_content']['league'][1]['teams']['count'];

for ($i = 0; $i < $num_teams; $i++) {
    $team = $league['fantasy_content']['league'][1]['teams'][$i]['team'];
    $team_key = $team[0][0]['team_key'];
    $url = "http://fantasysports.yahooapis.com/fantasy/v2/team/"
         . $team_key . "/roster;week=1?format=json";
    $data = oauth_request($url);
    $roster = json_decode($data, true);

    // check if team exists, grab revision
    $resp = $couch->send("GET","/rosters/$team_key");
    $existing_roster = json_decode($resp, true);
    if (array_key_exists('_rev',$existing_roster)) {
        // overwrite existing data
        $roster['_rev'] = $existing_roster['_rev'];
        $resp = $couch->send("PUT","/rosters/$team_key",json_encode($roster));
        print $resp;
    }
    else {
        $resp = $couch->send("PUT","/rosters/$team_key",json_encode($roster));
        print $resp;
    }
}
?>
