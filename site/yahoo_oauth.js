
function showTeams(obj, objName) {
  var result = "";
  var onlyOneTeam = false;
  var players_list = [];
  console.log(obj);
  for (var i in obj) {
      if (typeof obj[i] === null || typeof obj[i] !== "object") {
          continue;
      }
      if (obj instanceof Array) {
          var team = obj[i];
	  } else {
		  onlyOneTeam = true;
          var team = obj;
	  }
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
			var league_team = {"myteam": players_list}; 
			var league_number = "league" + num;
			sessionStorage.setItem(league_number, JSON.stringify(league_team));
			console.log(league_number, JSON.parse(sessionStorage.getItem(league_number)));
			getOtherPlayers(team.team_key, league_number);
			num += 1;
		  } else {
			alert("Your browser does not support web storage.  Please use a different browser to continue.");
		  }
	  }
	  if (onlyOneTeam) {
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
			var team_number = "other";
			
            
    		hello( network ).api('moreteams', 'get', qdata).then(function(m){
              console.log(m);
              var team = m;
              
              if (team.hasOwnProperty('team_key')) {
    			  for (var j in team.roster.players.player) {
    				players_list.push(team.roster.players.player[j].name.full);
    			  }
			  }
			  // Store other teams' players 
			  if (typeof(Storage) !== "undefined") {
					league_teams[team_number] = players_list;
					sessionStorage.setItem(league_number, JSON.stringify(league_teams));
					obj = JSON.parse(sessionStorage.getItem(league_number));
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
	setTimeout(function() {
	  console.log("Other Teams' Players", JSON.parse(sessionStorage.getItem(league_number)));
	}, 2000);
	
}

function loggedIn(network) {
  
  hello( network ).api('me').then(function(p){
	  document.getElementById('login').innerHTML = "<img src='"+ p.thumbnail + "' width=24/> Connected to "+ network+" as " + p.name;
  }).then(function(){
	  // Get team info
	  return hello( network ).api('teams');
  }).then(function(d){
	  document.getElementById('teamcontent').innerHTML = showTeams(d, "d");
  }).then(null, function(e){
	  console.error(e);
  });
  
}
function login(network){
  
	if (hello( network ).getAuthResponse()) {
	  loggedIn(network);
	} else {
		hello( network ).login().then(function(f){
		  for (var i in f){
			console.log("i", f[i]);
		  }
		// Get Profile
		return hello( network ).api('me');
		}).then(function(p){
			document.getElementById('login').innerHTML = "<img src='"+ p.thumbnail + "' width=24/> Connected to "+ network+" as " + p.name;
		}).then(function(){
			// Get team info
			return hello( network ).api('teams');
		}).then(function(d){
			document.getElementById('teamcontent').innerHTML = showTeams(d, "d");
		}).then(null, function(e){
			console.error(e);
		});
	}
  
	/*
	hello( network ).login().then(function(f){
		for (var i in f){
		  console.log("i", f[i]);
		}
		// Get Profile
		return hello( network ).api('me');
	}).then(function(p){
		document.getElementById('login').innerHTML = "<img src='"+ p.thumbnail + "' width=24/> Connected to "+ network+" as " + p.name;
	}).then(function(){
		// Get team info
		return hello( network ).api('teams');
	}).then(function(d){
		document.getElementById('teamcontent').innerHTML = showTeams(d, "d");
	}).then(null, function(e){
		console.error(e);
	});
	*/
}


hello.init({
	'yahoo' : 'dj0yJmk9T0dUclhxZXpRU2ExJmQ9WVdrOVdqVTJhekp6TXpZbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1hYQ--'
},
{
	redirect_uri:'http://kevinallen.github.io/waiver_coach/site/index.html',
	oauth_proxy: "https://auth-server.herokuapp.com/proxy"
});
