function json2table(json_url, table_id, col_config){
	$.getJSON(json_url, function(data) {
		
/*
		sessionStorage.setItem('current_wk_data', JSON.stringify(data));
		console.log('current_wk_data', JSON.parse(sessionStorage.getItem('current_wk_data')));
*/		

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
						class_str =  ' class="table_number"'
						//tbl_row += '<td class="table_number" align="right">'+v+'</td>'
					} else{
						class_str = ''
						//tbl_row += '<td>'+v+'</td>'
					}

					// link to player's page
					if(col === 'full_name'){
						v = '<a href="'+player_url(row)+'" target="_blank">'+v+'</a>'
					}
					tbl_row += '<td'+class_str+'>'+v+'</td>'
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
			features: {
        		paginate: false,
        		search: false,
        		recordCount: false
      		},
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
		
		//filter_table();
	})
}

col_config = {
	'type': {'displayName': 'Prediction', 'number':false},
	'rush_yards': {'displayName': 'Rush Yards', 'number':true, 'fixed_digits':2},
	'receiving_yards': {'displayName': 'Rec Yards', 'number':true, 'fixed_digits':2},
	'rush_tds': {'displayName': 'Rush TDs', 'number':true, 'fixed_digits':2},
	'receiving_tds': {'displayName': 'Rec TDs', 'number':true, 'fixed_digits':2},
	'receptions': {'displayName': 'Recs', 'number':true, 'fixed_digits':2},
	'rush_attempts': {'displayName': 'Rush Attempts', 'number':true, 'fixed_digits':2}
}

// TODO
// Make player names links to player page

json2table('../site_data/rmse_8_14.json', 'target_table', col_config)





