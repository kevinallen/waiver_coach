function showProps(obj, objName) {
  // var result = "";
  // for (var i in obj) {
  // console.log(obj[i]);
  //   if (obj.hasOwnProperty(i)) {
  //       result += objName + "." + i + " = " + obj[i] + "\n";
  //   }
  // }

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
      } else {
          var league = obj;
          result += "<h4>League</h4>";
          result += "<div><a href="+league.url+">"+league.name+"</a> "+league.league_key+"</div>";
          break;
      }


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
		document.getElementById('yahoocontent').innerHTML = showProps(d, "d");
	}).then(null, function(e){
		console.error(e);
	});
	// Get player info
	//hello( network ).api('players');
}


hello.init({
	'yahoo' : 'dj0yJmk9T0dUclhxZXpRU2ExJmQ9WVdrOVdqVTJhekp6TXpZbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1hYQ--'
},
{
	redirect_uri:'http://kevinallen.github.io/waiver_coach/site/index.html',
	oauth_proxy: "https://auth-server.herokuapp.com/proxy"
});
