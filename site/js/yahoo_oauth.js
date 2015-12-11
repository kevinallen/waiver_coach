

function showTeams(network) {
    hello( network ).api('myteams').then(function(teams){
        console.log(teams);
        document.getElementById("myteam").innerHTML = "";

        var onlyOneTeam = false;
        console.log(teams);
        for (var i in teams) {
          if (typeof teams[i] === null || typeof teams[i] !== "object") {
              continue;
          }
          if (teams instanceof Array) {
              var team = teams[i];
          } else {
        	  onlyOneTeam = true;
              var team = teams;
          }
          if (team.roster.players === null) {
        	  continue;
          }

          // display team on page, and keep track of all players in players_list
          var team_html = "<div class='col-sm-6'><h3 class=''>" + team.name + "</h3><p class='team'>";
          var players = team.roster.players.player;
          for (var j in players) {
              var player = players[j];
              var name = player.display_position == "DEF" ? player.name.first : player.name.first.substring(0,1) + ". " + player.name.last;
              team_html += name + " - <span class='team-players'>" + player.display_position + "</span><br/>";
          }
          team_html += "</p></div>";
          document.getElementById("myteam").innerHTML += team_html;

          if (onlyOneTeam) {
        	break;
          }
        }
        $('#myteam').show();
    });
}

function parseLeagues(leagues, network) {
    var onlyOneLeague = false;

    for (var i in leagues) {
        if (leagues instanceof Array) {
          league = leagues[i];
        } else {
          league = leagues;
          onlyOneLeague = true;
        }

        if (league.draft_status != "postdraft") {
            continue;
        }

        // get league names
        hello(network).api('league_name', 'get', {league_key: league.league_key}).then(function(league){
            if (typeof(Storage) !== "undefined") {
                var current_leagues = JSON.parse(sessionStorage.getItem("leagues"));
                if (current_leagues == null) {
                    current_leagues = {};
                }
                current_leagues[league.league_key] = league.name;
                sessionStorage.setItem("leagues", JSON.stringify(current_leagues));
                console.log("leagues", JSON.parse(sessionStorage.getItem("leagues")));
            } else {
                alert("Your browser does not support web storage.  Please use a different browser to continue.");
            }
        });

        for (var i = 1; i <= Number(league.num_teams); i++) {
            var teamID = league.league_key + ".t." + i;
            var qdata = {team: teamID};

            console.log("Getting players for: " + teamID);
            hello( network ).api('players', 'get', qdata).then(function(team){
                if (team.roster.players == null) {
                    return;
                }
                var key = team.team_key.split(".t")[0];

                // get running backs in this league from storage
                var current_players = [];
                var all_players = JSON.parse(sessionStorage.getItem("running_backs"));
                if (all_players != null) {
                    if (key in all_players) {
                        current_players = all_players[key];
                    }
                } else {
                    all_players = {};
                }

                var players = team.roster.players.player;
                for (var j in players) {
                    var player = players[j];
                    if (player.display_position == "RB") {
                        current_players.push(player.name.full);
                    }
                }

                all_players[key] = current_players;
                // Store all running backs in league
                if (typeof(Storage) !== "undefined") {
                    sessionStorage.setItem("running_backs", JSON.stringify(all_players));
                    console.log("running_backs", JSON.parse(sessionStorage.getItem("running_backs")));
                } else {
                    alert("Your browser does not support web storage.  Please use a different browser to continue.");
                }
            }).then(null, function(e){
              console.error(e);
            });
        }

        if (onlyOneLeague) {
            break;
        }
    }
}

function getInjuredPlayers(network) {
    // get injury status
    for (var i=0; i <= 500; i += 25) {
        hello(network).api('all_players', 'get', {start: i}).then(function(players){

            var statuses = ["IR","O"];
            var all_injured_players = JSON.parse(sessionStorage.getItem("injured_players"));
            if (all_injured_players == null) {
                all_injured_players = [];
            }

            console.log(players);
            for (var i in players) {
                var player = players[i];
                if ("status" in player && player.display_position == "RB") {
                    console.log("potential injury");
                    // check if this player is injured and keep track of all injured players
                    if (statuses.indexOf(player.status) > -1) {
                        all_injured_players.push(player.name.full);
                    }
                }
            }

            sessionStorage.setItem("injured_players", JSON.stringify(all_injured_players));
            console.log("injured_players", JSON.parse(sessionStorage.getItem("injured_players")));

        });
    }
}

function login(network){

	if (!hello( network ).getAuthResponse()) {
		hello( network ).login().then(function(f){
		// Get Profile
		return hello( network ).api('me');
		}).then(function(p){
		    $(".login-button").addClass("currently-displayed");
            $(".login-button").html("Connected to Yahoo!");
            $("#signin").html(p.first_name).addClass("bold");
            if (typeof(Storage) !== "undefined") {
                sessionStorage.setItem("me", JSON.stringify(p));
                console.log("me", JSON.parse(sessionStorage.getItem("me")));
            } else {
                alert("Your browser does not support web storage.  Please use a different browser to continue.");
            }
		}).then(function(){
			// Get leagues for player
			return hello( network ).api('league');
		}).then(function(d){
            parseLeagues(d, network);
            showTeams(network);
            getInjuredPlayers(network);
		}).then(null, function(e){
			console.error(e);
		});
	}
}

$(document).ready(function() {
    if (hello( 'yahoo' ).getAuthResponse()) {
        showTeams('yahoo');
        $(".login-button").addClass("currently-displayed");
        $(".login-button").html("Connected to Yahoo!");

        if (typeof(Storage) !== "undefined") {
            var me = JSON.parse(sessionStorage.getItem("me"));
            $("#signin").html(me.first_name).addClass("bold");
        } else {
            alert("Your browser does not support web storage.  Please use a different browser to continue.");
        }
    }
});

hello.init({
	'yahoo' : 'dj0yJmk9T0dUclhxZXpRU2ExJmQ9WVdrOVdqVTJhekp6TXpZbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1hYQ--'
},
{
	redirect_uri:'http://kevinallen.github.io/waiver_coach/site/index.html',
	oauth_proxy: "https://auth-server.herokuapp.com/proxy"
});

// function used to test display of a user's teams, useful to develop locally
// before using this, need to save the object myteams.json to the site root
function test() {
    document.getElementById("myteam").innerHTML = "";
    $(".login-button").addClass("currently-displayed");
    $(".login-button").html("Connected to Yahoo!");
    $.getJSON("myteams.json", function(teams) {
        sessionStorage.setItem("myteams", teams);
        for (var i in teams) {
            // skip this team if there are no players
            var team = teams[i];
            if (team.roster.players === null) {
                continue;
            }
            console.log(team);
            var team_html = "<div class='col-sm-6'><h3 class=''>" + team.name + "</h3><p class='team'>";
            var players = team.roster.players.player;
            for (var j in players) {
                var player = players[j];
                var name = player.display_position == "DEF" ? player.name.first : player.name.first.substring(0,1) + ". " + player.name.last;
                team_html += name + " - <span class='team-players'>" + player.display_position + "</span><br/>";
            }
            team_html += "</p></div>";
            console.log(team_html);
            document.getElementById("myteam").innerHTML += team_html;
            $('#myteam').show();
        }
    });
}
