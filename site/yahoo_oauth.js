
			
function login(network){
	hello( network ).login().then(function(){
		// Get Profile
		return hello( network ).api('me');
	}).then(function(p){
		document.getElementById('login').innerHTML = "<img src='"+ p.thumbnail + "' width=24/>Connected to "+ network+" as " + p.name;
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
			
