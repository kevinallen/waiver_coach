function showProps(obj, objName) {
  var result = "";
  for (var i in obj) {
	console.log(obj[i]);
    if (obj.hasOwnProperty(i)) {
        result += objName + "." + i + " = " + obj[i] + "\n";
    }
  }
  return result;
}
			
function login(network){
	hello( network ).login().then(function(){
		// Get Profile
		return hello( network ).api('me');
	}).then(function(p){
		document.getElementById('login').innerHTML = "<img src='"+ p.thumbnail + "' width=24/>Connected to "+ network+" as " + p.name;
		document.getElementById('yahoocontent').innerHTML = showProps(p, "p");	
	}).then(function(){
		// Get league info
		return hello( network ).api('league');
	}).then(function(d){
		document.getElementById('yahoocontent').innerHTML = showProps(d, "d");  
	}).then(null, function(e){
		console.error(e);
	});
}


hello.init({
	'yahoo' : 'dj0yJmk9ZFZkc2FkaVBEQ0dPJmQ9WVdrOU5HaGxVazFOTnpJbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD04Zg--' 
},
{
	redirect_uri:'index.html',
	oauth_proxy: "https://auth-server.herokuapp.com/proxy"
});
			
