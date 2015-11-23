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

function showTeams(obj, objName) {
  var result = "";
  console.log(obj);
  for (var i in obj) {
      if (typeof obj[i] === null || typeof obj[i] !== "object") {
          continue;
      }
      if (obj instanceof Array) {
          var team = obj[i];
          if (!team.roster.players.hasOwnProperty('player')) {
              continue;
          }
          result += "<h4>Team "+i+"</h4>";
          if (team.hasOwnProperty('team_key')) {
              result += "<div><a href="+team.url+">"+team.name+"</a> "+team.team_key+"</div>";
			  for (var j in team.roster.players.player) {
				result += "<div>" + team.roster.players.player[j].eligible_positions.position + " - "+team.roster.players.player[j].name.full+"</a> "+"</div>";
			  }
          }
		  result += '<button id="players" onclick="players();">Show Players</button>';
      } else {
          var team = obj;
          if (!team.roster.players.hasOwnProperty('player')) {
              break;
          }
          result += "<h4>Team</h4>";
          result += "<div><a href="+team.url+">"+team.name+"</a> "+team.team_key+"</div>";
          for (var j in team.roster.players.player) {
              result += "<div>" + team.roster.players.player[j].eligible_positions.position + " - "+team.roster.players.player[j].name.full+"</a> "+"</div>";
          }
      }
  }
  return result;
}


function showPlayers(obj, objName) {
  var result = "";
  console.log(obj);
  result += "<h4>Players</h4>";
  for (var i in obj) {
      if (typeof obj[i] === null || typeof obj[i] !== "object") {
          continue;
      }
	  var player = obj[i];
	  console.log(player);
	  result += "<div>" + player.eligible_positions.position + " - "+player.name.full+"</a> "+"</div>";

  }
  return result;
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
