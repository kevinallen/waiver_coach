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
          if (team.roster.players === null) {
              continue;
          }
          result += "<h4>Team "+i+"</h4>";
          if (team.hasOwnProperty('team_key')) {
              result += "<div><a href="+team.url+">"+team.name+"</a> "+team.team_key+"</div>";
			  for (var j in team.roster.players.player) {
				result += "<div>" + team.roster.players.player[j].eligible_positions.position + " - "+team.roster.players.player[j].name.full+"</a> "+"</div>";
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
			sessionStorage.setItem("t1", players_list);
			console.log(sessionStorage.getItem("t1"));
			getOtherPlayers(team.team_key);
		  } else {
			alert("Your browser does not support web storage.  Please use a different browser to continue.");
		  }
          break;
      }
  }
  return result;
}

function getOtherPlayers(team_key) {
    var myTeam = Number(team_key.split("t.")[1]);  // Get user's team number
	var network = 'yahoo';
	hello( network ).api('league').then(function(d){
	  console.log(d);
	  console.log(d.num_teams);
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

hello.init({
	'yahoo' : 'dj0yJmk9T0dUclhxZXpRU2ExJmQ9WVdrOVdqVTJhekp6TXpZbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1hYQ--'
},
{
	redirect_uri:'http://kevinallen.github.io/waiver_coach/site/index.html',
	oauth_proxy: "https://auth-server.herokuapp.com/proxy"
});
