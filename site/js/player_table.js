function player_url(player_row){
	return("player_details.html?player_id="+player_row['player_id'])
}

function json2table(json_url, table_id, col_config){
	$.getJSON(json_url, function(data) {
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
			$.each(cols, function(i, col){
				var config = col_config[col]
				var v = row[col]
				if(config){
					if(config['number']){
						v = parseFloat(v).toFixed(config['fixed_digits'])
						//tbl_row += '<td class="table_number" align="right">'+v+'</td>'	
					} else{
						//tbl_row += '<td>'+v+'</td>'		
					}

					// link to player's page
					if(col === 'full_name'){
						v = '<a href="'+player_url(row)+'">'+v+'</a>'
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
		})

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
	})
}

col_config = {
	'full_name': {'displayName': 'Name', 'number':false},
	'rushing_att': {'displayName': 'Rush Att', 'number':true, 'fixed_digits':0},
	'rushing_yds': {'displayName': 'Rush Yards', 'number':true, 'fixed_digits':0},
	'rushing_tds': {'displayName': 'Rush TDs', 'number':true, 'fixed_digits':2},
	'receiving_rec': {'displayName': 'Receptions', 'number':true, 'fixed_digits':0},
	'receiving_yds': {'displayName': 'Rec Yards', 'number':true, 'fixed_digits':0},
	'receiving_tds': {'displayName': 'Rec TDs', 'number':true, 'fixed_digits':2},
}

// TODO
// Make player names links to player page

json2table('predictions.json', 'target_table', col_config)
