function player_url(player_row){
	//return("player_details.html?player_id="+player_row['player_id'])
	return("index.html?player1="+player_row['player_id']+'#distribution')
}

function player_points(player_row, col_config){
	var totalpoints = 0;
	$.each(Object.keys(col_config), function(i, col){
		var config = col_config[col]
		if(config){
			var fpoints = config['fpoints']
			if(fpoints){
				var statvalue = parseFloat(player_row[col])
				totalpoints += statvalue * fpoints
			}
		}
	})
	return(totalpoints)
}

function json2table(json_url, table_id, col_config){
	$.getJSON(json_url, function(data) {
		sessionStorage.setItem('current_wk_data', JSON.stringify(data));
		console.log('current_wk_data', JSON.parse(sessionStorage.getItem('current_wk_data')));
		var tbl_body = '';
		var tbl_head = '<tr>'
		var cols = Object.keys(col_config)
		var col_display = {}
		$.each(cols, function(i, col){
			var config = col_config[col]
			if(config){
				var col_head = ''
				if(config['displayName']){
					col_head = config['displayName']
				} else{
					col_head = col
				}
				col_display[col] = col_head

				if(config['number']){
					// add header for number rows for different formatting (float right)
					tbl_head += '<th class="table_number">'+col_head+'</th>'
				} else{
					tbl_head += '<th>'+col_head+'</th>'
				}

			}

		})
		tbl_head += '</tr>'

		$.each(data, function(){
			var tbl_row = '';
			var row = this;
			var fpoints = 0;

			$.each(cols, function(i, col){
				var config = col_config[col]

				if(config){
					

					if(config['calculate_points']){
						var v = String(player_points(row, col_config))
					} else{
						var v = row[col]
					}

					if(config['number']){
						v = parseFloat(v)
						v = v.toFixed(config['fixed_digits'])
						
						//tbl_row += '<td class="table_number" align="right">'+v+'</td>'
					} else{

						//tbl_row += '<td>'+v+'</td>'
					}

					// link to player's page
					if(col === 'full_name'){
						v = '<a href="'+player_url(row)+'" target="_blank">'+v+'</a>'
					}
					tbl_row += '<td>'+v+'</td>'
				}
			})
			tbl_body += "<tr>"+tbl_row+'</tr>'
		})

		var sortTypeObj = {}
		$.each(cols, function(i, col){
			if(col_config[col]['number']){
				sortTypeObj[col_display[col].toLowerCase()] = 'number'
			}
		});

		$('#'+table_id+' thead').html(tbl_head)
		$('#'+table_id+' tbody').html(tbl_body)
		$('#'+table_id).dynatable({
			table: {
			    defaultColumnIdStyle: 'lowercase',
			    copyHeaderClass: true, // copies <th> class to cells
			    copyClass: true
			  },
			dataset: {
				sortTypes: sortTypeObj,
				perPageDefault: 50,
    			perPageOptions: [20,50,100,200]
			}
		});
		filter_table();
	})
}

col_config = {
	'full_name': {'displayName': 'Name', 'number':false},
	'calculate_points': {'displayName': 'Points', 'calculate_points': true, 'number':true, 'fixed_digits':2},
	'rushing_att': {'displayName': 'Rush Att', 'number':true, 'fixed_digits':0, 'fpoints':0},
	'rushing_yds': {'displayName': 'Rush Yards', 'number':true, 'fixed_digits':0, 'fpoints':0.1},
	'rushing_tds': {'displayName': 'Rush TDs', 'number':true, 'fixed_digits':2, 'fpoints':6},
	'receiving_rec': {'displayName': 'Receptions', 'number':true, 'fixed_digits':0, 'fpoints':0},
	'receiving_yds': {'displayName': 'Rec Yards', 'number':true, 'fixed_digits':0, 'fpoints':0.1},
	'receiving_tds': {'displayName': 'Rec TDs', 'number':true, 'fixed_digits':2, 'fpoints':6},
}

// TODO
// Make player names links to player page

json2table('../site_data/predictions.json', 'target_table', col_config)

function filter_table() {
	var taken_players = JSON.parse(sessionStorage.getItem("running_backs"));
	console.log("taken_players", taken_players);
	var injured_players = JSON.parse(sessionStorage.getItem("injured_players"));
	console.log("injured_players", injured_players);

	var selected_league = "";
	$("#league_select option:selected").each(function(){
		selected_league = $(this).val();
	});
	console.log("selected_league", selected_league);

	var unavailable_players = [];
	if (taken_players) {
		if (selected_league in taken_players) {
			unavailable_players = taken_players[selected_league];
		}
	}

	unavailable_players = unavailable_players.concat(injured_players);
	console.log("unavailable_players", unavailable_players);

	var dynatable = $('#target_table').data('dynatable');

	dynatable.queries.add("name", "");
	dynatable.queries.functions['name'] = function(record, queryValue) {
		return unavailable_players.indexOf(record['dynatable-sortable-text'].name) == -1;
	};

	dynatable.process();
}

$('#filter_rb').click(function() {

	// make dropdown visible
	$('.league_div').toggle();

	// get leagues and add to dropdown
	var leagues = JSON.parse(sessionStorage.getItem("leagues"));
	console.log("leagues", leagues);

	$.each(leagues, function(key, val) {
		// select and modify the HTML5 template
		var template = document.querySelector('#league_template').content;
		var option = template.querySelector('#option');
		option.value = key;
		option.textContent = val;
		// append template to DOM
		var clone = document.importNode(template, true);
		var oldcontent = document.querySelector('#league_select');
		oldcontent.appendChild(clone);
	});

	if ($('#filter_rb').is(':checked')) {
		filter_table();
	}
	else {
		document.querySelector('#league_select').innerHTML = '';
	}
});

$('#league_select').on('change', function() {
	filter_table();
});

$(document).ready(function() {
	var data = JSON.parse(sessionStorage.getItem('current_wk_data'));
	document.getElementById('include_week').innerHTML='Week ' + data[0].week + ' ';
});
