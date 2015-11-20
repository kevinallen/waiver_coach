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
	  result += "<div>" + player.eligible_positions.position + " - <a href="+player.image_url+">"+player.name.full+"</a> "+"</div>";

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
		// Get league info
		return hello( network ).api('league');
	}).then(function(d){
		document.getElementById('leaguecontent').innerHTML = showProps(d, "d");
	}).then(null, function(e){
		console.error(e);
	});
	  
}

function players(){
	// Get player info
	network = 'yahoo'
	/*
	hello( network ).login().then(function(){
		return hello( network ).api('me')
	}).then(function(){
		return
	*/  
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
