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
		/*
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
		*/
		//filter_table();
	})
}

col_config = {
	'stat': {'displayName': 'Statistic', 'number':false},
	'Historical': {'displayName': 'Historical', 'number':true, 'fixed_digits':2},
	'CBS': {'displayName': 'CBS', 'number':true, 'fixed_digits':2},
	'ESPN': {'displayName': 'ESPN', 'number':true, 'fixed_digits':2},
	'FFToday': {'displayName': 'FF Today', 'number':true, 'fixed_digits':2},
	'Expert': {'displayName': 'Expert', 'number':true, 'fixed_digits':2},
	'HistoricalAndExpert': {'displayName': 'Historical + Expert', 'number':true, 'fixed_digits':2},
}

// TODO
// Make player names links to player page

json2table('../site_data/rmse_8_14.json', 'target_table', col_config)





