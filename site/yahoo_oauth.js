/*
function showProps(obj, objName) {
  var result = "";
  console.log(obj);
  for (var i in obj) {
      if (typeof obj[i] === null || typeof obj[i] !== "object") {
          continue;
      }
      if (obj instanceof Array) {
          var league = obj[i];
          result += "<h4>League "+i+"</h4>";
          console.log(league);
          if (league.hasOwnProperty('league_key')) {
              result += "<div><a href="+league.url+">"+league.name+"</a> "+league.league_key+"</div>";
          }
		  result += '<button id="players" onclick="players();">Show Players</button>';
      } else {
          var league = obj;
          result += "<h4>League</h4>";
          result += "<div><a href="+league.url+">"+league.name+"</a> "+league.league_key+"</div>";
		  result += '<button id="players" onclick="players();">Show Players</button>';
          break;
      }


  }
  return result;
}
*/
function showTeams(obj, objName) {
  var result = "";
  var players_list = [];
  console.log(obj);
  for (var i in obj) {
      if (typeof obj[i] === null || typeof obj[i] !== "object") {
          continue;
      }
      if (obj instanceof Array) {
          var team = obj[i];
		  var num = 1;
          if (team.roster.players === null) {
              continue;
          }
          result += "<h4>Team "+i+"</h4>";
          if (team.hasOwnProperty('team_key')) {
              result += "<div><a href="+team.url+">"+team.name+"</a> "+team.team_key+"</div>";
			  for (var j in team.roster.players.player) {
				result += "<div>" + team.roster.players.player[j].eligible_positions.position + " - "+team.roster.players.player[j].name.full+"</a> "+"</div>";
				players_list.push(team.roster.players.player[j].name.full);
			  }
			  if (typeof(Storage) !== "undefined") {
				var league_team = ("t0", players_list);
				var league_number = "league" + num;
				sessionStorage.setItem(league_number, league_team);
				//sessionStorage.setItem("t0", players_list);
				console.log(sessionStorage.getItem(league_number));
				getOtherPlayers(team.team_key, league_number);
				num += 1;
			  } else {
				alert("Your browser does not support web storage.  Please use a different browser to continue.");
			  }
          }

      } else {
          var team = obj;
          if (team.roster.players === null) {
              break;
          }
          result += "<h4>Team</h4>";
          result += "<div><a href="+team.url+">"+team.name+"</a> "+team.team_key+"</div>";
          for (var j in team.roster.players.player) {
              result += "<div>" + team.roster.players.player[j].eligible_positions.position + " - "+team.roster.players.player[j].name.full+"</a> "+"</div>";
			  players_list.push(team.roster.players.player[j].name.full);
		  }
		  if (typeof(Storage) !== "undefined") {
			var league_team = {"t0":players_list};
			sessionStorage.setItem("league1", JSON.stringify(league_team));
			//sessionStorage.setItem("t0", players_list);
			console.log("league1", JSON.parse(sessionStorage.getItem("league1")));
			getOtherPlayers(team.team_key, "league1");
		  } else {
			alert("Your browser does not support web storage.  Please use a different browser to continue.");
		  }
          break;
      }
  }
  return result;
}

function getOtherPlayers(team_key, league_number) {
	var myLeague = team_key.split(".t")[0];  		// Get user's League number
    var myTeam = Number(team_key.split("t.")[1]);   // Get user's team number
	var network = 'yahoo';
	var players_list = [];
	hello( network ).api('league').then(function(d){
	  var onlyOneLeague = false;
      for (var j in d) {
          
		  if (d instanceof Array) {
			league = d[j];
		  } else {
			league = d;
			onlyOneLeague = true;
		  }
		 // if (typeof d[j] === null || typeof d[j] !== "object") {
         // continue;
		 // }
		  
          if (league.draft_status != "postdraft") {
              continue;
          }
    	  for (var i = 1; i <= Number(league.num_teams); i++) {
    		if (i == myTeam) {
    		  continue;
    		}
    		var teamID = myLeague + ".t." + i;
    	    var qdata = {team: teamID};
            var result = "";
			players_list = [];
			var league_teams = {};
			var number = i;
			var team_number = "";
            
    		hello( network ).api('moreteams', 'get', qdata).then(function(m){
              console.log(m);
              var team = m;
              //result += "<h4>"+team.name+"</h4>";
              if (team.hasOwnProperty('team_key')) {
    			  for (var j in team.roster.players.player) {
    				//result += "<div>" + team.roster.players.player[j].eligible_positions.position + " - "+team.roster.players.player[j].name.full+"</a> "+"</div>";
    				players_list.push(team.roster.players.player[j].name.full);
    			  }
				  team_number = "t" + number;
				  league_teams[team_number] = players_list;
				  for (var l in league_teams){
					  console.log(l, league_teams[l]);
					}
              }
			  if (typeof(Storage) !== "undefined") {
    				sessionStorage.setItem(league_number, JSON.stringify(league_teams));
					obj = JSON.parse(sessionStorage.getItem(league_number));
					for (var o in obj){
					  console.log(o, obj[o]);
					}
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
	}).then(null, function(e){
		console.error(e);
	});
}

function login(network){
	hello( network ).login().then(function(){
		// Get Profile
		return hello( network ).api('me');
	}).then(function(p){
		document.getElementById('login').innerHTML = "<img src='"+ p.thumbnail + "' width=24/> Connected to "+ network+" as " + p.name;
		//document.getElementById('yahoocontent').innerHTML = showProps(p, "p");
	}).then(function(){
		// Get team info
		return hello( network ).api('teams');
	}).then(function(d){
		document.getElementById('teamcontent').innerHTML = showTeams(d, "d");
	}).then(null, function(e){
		console.error(e);
	});
}

function players(){
	// Get player info
	network = 'yahoo'

	hello( network ).api('players').then(function(d){
		document.getElementById('rostercontent').innerHTML = showPlayers(d,"d");
	}).then(null, function(e){
		console.error(e);
	});
}

hello.init({
	'yahoo' : 'dj0yJmk9T0dUclhxZXpRU2ExJmQ9WVdrOVdqVTJhekp6TXpZbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1hYQ--'
},
{
	redirect_uri:'http://kevinallen.github.io/waiver_coach/site/index.html',
	oauth_proxy: "https://auth-server.herokuapp.com/proxy"
});
