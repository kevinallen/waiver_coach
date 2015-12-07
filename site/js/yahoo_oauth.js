

function showTeams(teams) {
  var result = "";
  document.getElementById("myteam").innerHTML = "";
  var onlyOneTeam = false;
  var players_list = [];
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
      console.log(team);
      // display team on page, and keep track of all players in players_list
      var team_html = "<div class='col-sm-6'><h3 class=''>" + team.name + "</h3><p class='team'>";
      var players = team.roster.players.player;
      for (var j in players) {
          var player = players[j];
          players_list.push(team.roster.players.player[j].name.full);
          var name = player.display_position == "DEF" ? player.name.first : player.name.first.substring(0,1) + ". " + player.name.last;
          team_html += name + " - <span class='team-players'>" + player.display_position + "</span><br/>";
      }
      team_html += "</p></div>";
      document.getElementById("myteam").innerHTML += team_html;
      $('#myteam').show();

      // put players_list in session storage and grab players from other teams
	  if (typeof(Storage) !== "undefined") {
		var league_team = {"myteam": players_list};
		sessionStorage.setItem(team.name, JSON.stringify(league_team));
		console.log(team.name, JSON.parse(sessionStorage.getItem(team.name)));
	  } else {
		alert("Your browser does not support web storage.  Please use a different browser to continue.");
	  }

	  if (onlyOneTeam) {
		break;
	  }
  }
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

        for (var i = 1; i <= Number(league.num_teams); i++) {
            var teamID = league.league_key + ".t." + i;
            var qdata = {team: teamID};

            console.log("Getting players for: " + teamID);
            hello( network ).api('players', 'get', qdata).then(function(team){
                if (team.roster.players == null) {
                    return;
                }
                var key = team.team_key.split(".t")[0];
                var current_players = [];
                var all_players = JSON.parse(sessionStorage.getItem(key));
                if (all_players != null) {
                    current_players = all_players;
                }

                var players = team.roster.players.player;
                for (var j in players) {
                    var player = players[j];
                    if (player.display_position == "RB") {
                        current_players.push(player.name.full);
                    }
                }
                // Store all running backs in league
                if (typeof(Storage) !== "undefined") {
                    sessionStorage.setItem(key, JSON.stringify(current_players));
                    console.log(key, JSON.parse(sessionStorage.getItem(key)));
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

// function getOtherPlayers(team_key) {
// 	var myLeague = team_key.split(".t")[0];  		// Get user's League number
//     var myTeam = Number(team_key.split("t.")[1]);   // Get user's team number
// 	var network = 'yahoo';
// 	var players_list = [];
// 	hello( network ).api('league').then(function(d){
// 	  var onlyOneLeague = false;
//       for (var j in d) {
//
// 		  if (d instanceof Array) {
// 			league = d[j];
// 		  } else {
// 			league = d;
// 			onlyOneLeague = true;
// 		  }
//
//           if (league.draft_status != "postdraft") {
//               continue;
//           }
//     	  for (var i = 1; i <= Number(league.num_teams); i++) {
//     		// if (i == myTeam) {
//     		//   continue;
//     		// }
//     		var teamID = myLeague + ".t." + i;
//     	    var qdata = {team: teamID};
//
//     		hello( network ).api('moreteams', 'get', qdata).then(function(m){
//               var team = m;
//               var players = team.roster.players.player;
//     		  for (var j in players) {
//                 var player = players[j];
//                 if (player.display_position = "RB") {
//                   players_list.push(player.name.full);
//                 }
//               }
//               // Store other teams' players
//               if (typeof(Storage) !== "undefined") {
//                 league_teams[team_name] = players_list;
//                 sessionStorage.setItem(myLeague, JSON.stringify(players_list));
//                 console.log(myLeague, JSON.parse(sessionStorage.getItem(myLeague)));
//               } else {
//                 alert("Your browser does not support web storage.  Please use a different browser to continue.");
//               }
//             }).then(null, function(e){
//               console.error(e);
//             });
//     	  }
//
// 		  if (onlyOneLeague) {
// 			break;
// 		  }
// 	  }
// 	}).then(null, function(e){
// 		console.error(e);
// 	});
// 	setTimeout(function() {
// 	  console.log("Other Teams' Players", JSON.parse(sessionStorage.getItem(myLeague)));
// 	}, 2000);
//
// }

function loggedIn(network) {

  hello( network ).api('me').then(function(p){
	  // Get team info
	  return hello( network ).api('teams');
  }).then(function(p){
      $(".login-button").addClass("currently-displayed");
      $(".login-button").html("Connected to Yahoo!");
  }).then(function(){
      // Get team info
      return hello( network ).api('teams');
  }).then(function(d){
      showTeams(d);
      //sessionStorage.setItem("myteams", d);
  }).then(null, function(e){
      console.error(e);
  });
}

function login(network){

	if (hello( network ).getAuthResponse()) {
	  //loggedIn(network);
	} else {
		hello( network ).login().then(function(f){
		  for (var i in f){
			console.log("i", f[i]);
		  }
		// Get Profile
		return hello( network ).api('me');
		}).then(function(p){
		    $(".login-button").addClass("currently-displayed");
            $(".login-button").html("Connected to Yahoo!");
		}).then(function(){
			// Get leagues for player
			return hello( network ).api('league');
		}).then(function(d){
            parseLeagues(d, network);
		}).then(null, function(e){
			console.error(e);
		});
	}
}

$(document).ready(function() {
    if (hello( 'yahoo' ).getAuthResponse()) {
        loggedIn('yahoo');
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
