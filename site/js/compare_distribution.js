
var margin = {top: 20, right: 20, bottom: 40, left: 50},
    width = 600 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

var x = d3.scale.linear()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var color = d3.scale.category10();

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var line = d3.svg.line()
    .x(function(d) { return x(d.x); })
    .y(function(d) { return y(d.y); });

var svg = d3.select("#plot").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var GLOBAL_data;
// initial players

var GLOBAL_players = initial_players()//['00-0023500',''];

d3.json("../site_data/distdata/2015_10.json", function(error, data) {
  
  if (error) throw error;

  //######## SET UP

  // initialize menus
  create_player_menu(data)
  
  create_plot(data, ['',''])

  GLOBAL_data = data

  update_plot(data, GLOBAL_players)

});

//#####################
// FUNCTIONS

var empty_player = function(data){
  if( data === undefined){
    smooth = [{'x':0, 'y':0},{'x':0, 'y':0}]
  } else{
    smooth = _.map(data[_.keys(data)[0]]['smooth'], function(d){return {'x':0, 'y':0}})
  }
  player_info = {'standard_score':0}

  return {'player_id':'', 'player_name':'', 'smooth':smooth, 'player_info':player_info}
}

var collect_player_data = function(data, players){
  // this functions picks out the keys in players
  // formats the objects, and adds the player_id

  var player_data = _.map(players, function(p){
    obj = p ===''? empty_player(data): data[p]
    obj.smooth = _.map(obj.smooth, function(d){return {'x':+d.x, 'y':+d.y}})
    return obj
  })

  return player_data
}

var combine_player_data = function(data, players){
  // this function combines the "smooth" series for the keys in players
  var combined_player_data = _.reduce(collect_player_data(data,players), function(memo, d){
    return memo.concat(d['smooth']); 
  }, []);
  return combined_player_data
}

var update_menu_display = function(display, which_menu){
  $('#'+which_menu).val(display)
}

var update_all_menu_displays = function(displays){
  update_menu_display(displays[0], 'player1_menu')
  update_menu_display(displays[1], 'player2_menu')
}

var create_player_menu = function(data){
  var menu_data = _.map(_.values(data), function(d){
    return {'label':d.player_name, 'value':d.player_id}
  })

  $('#player1_menu').autocomplete({
    source: menu_data,
    select: function (event, ui){
      update_menu_display(ui.item.label, 'player1_menu')
      GLOBAL_players[0] = ui.item? ui.item.value: ''
      update_plot(GLOBAL_data, GLOBAL_players)
      return false
    },
    change: function (event, ui){
      if(!ui.item){
        GLOBAL_players[0] = ''
        update_plot(GLOBAL_data, GLOBAL_players)
      }
      return false
    },
    focus: function(event, ui){
      return false
    }
  })
  $('#player2_menu').autocomplete({
    source: menu_data,
    select: function (event, ui){
      update_menu_display(ui.item.label, 'player2_menu')
      GLOBAL_players[1] = ui.item? ui.item.value: ''
      update_plot(GLOBAL_data, GLOBAL_players)
      return false
    },
    change: function (event, ui){
      if(!ui.item){
        GLOBAL_players[1] = ''
        update_plot(GLOBAL_data, GLOBAL_players)
      }
      //return false
    },
    focus: function(event, ui){
      return false
    }
  })

  d3.select('#player1_menu').style('background-color', color.range()[0])
  d3.select('#player2_menu').style('background-color', color.range()[1])
}


var update_color = function(data, players){
  color.domain(players)
}

var update_axis_domain = function(data, players){
  var combined_player_data = combine_player_data(data, players)
  x.domain(d3.extent(combined_player_data, function(d) { return d.x; }));
  y.domain(d3.extent(combined_player_data, function(d) { return d.y; }));
}

var create_x_axis = function(){
  svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
      .append('text')
        .attr('transform', 'translate('+width/2 +',30)')
        .style("text-anchor", "middle")
        .text('Standard Fantasy Points');

}

var create_y_axis = function(){
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Density");
}

var create_lines = function(data, players){
  var player = svg.selectAll('.player')
    .data(collect_player_data(data, players))
    .enter()
    .append('g')
    .attr('class', 'player')

  player.append('path')
    .attr('class','line')
    .attr("d", function(d){
      return line(d.smooth)
    })
    .style('stroke', function(d){ return color(d.player_id)});

  player.append('line')
    .attr('class','vline')
    .attr('y1', 0)
    .attr('y2', height)
    .attr('x1', function(d){return x(d.player_info.standard_score)})
    .attr('x2', function(d){return x(d.player_info.standard_score)})

}

var update_x_axis = function(ms){
  svg.select('g.x.axis').transition().duration(ms).call(xAxis)
}
var update_y_axis = function(ms){
  svg.select('g.y.axis').transition().duration(ms).call(yAxis)
}
var update_lines = function(data, players, ms){
  var el_players = svg.selectAll('.player')
    .data(collect_player_data(data, players))
    
  
  el_players.select('path')
    .style('stroke', function(d){ return color(d.player_id)})
    .transition().duration(ms)
    .attr("d", function(d){
      return line(d.smooth)
    })
    .style('opacity', function(d){
      return d.player_name === '' ? 0 : 1
    })

  el_players.select('.vline')
    .style('stroke', function(d){ return color(d.player_id)})
    .transition().duration(ms)
    .attr('y1', 0)
    .attr('y2', height)
    .attr('x1', function(d){return x(d.player_info.standard_score)})
    .attr('x2', function(d){return x(d.player_info.standard_score)})
    .style('opacity', function(d){
      return d.player_name === '' ? 0 : 1
    })
}

var create_plot = function(data, players){
  // bind color for players
  update_color(data, players)

  // set axis domain from player data
  update_axis_domain(data, players)

  // create axes
  create_x_axis()
  create_y_axis()

  // create plot lines
  create_lines(data, players)
  create_prompt_text()
  update_prompt_text(players)
}

var update_plot = function(data, players, transition_duration){
  if( transition_duration === undefined){
    transition_duration = 2000
  }

  // bind color for players
  update_color(data, players)

  // set axis domain from player data
  update_axis_domain(data, players)

  // update axes
  update_x_axis(transition_duration)
  update_y_axis(transition_duration)

  // update lines
  update_lines(data, players, transition_duration)

  collected_data = collect_player_data(data, players)

  update_all_menu_displays(_.pluck(collected_data,'player_name'))

  update_prompt_text(players,transition_duration/2)
}

function create_prompt_text(){
  svg.append('g')
  .attr('class', 'prompt_text')
  .append('text')
        .attr('transform', 'translate('+width/2 +','+height/2+')')
        .style("text-anchor", "middle")
        .text('Enter Player Names in the Text Boxes to Get Started')
  
}

function update_prompt_text(players, transition_duration){
  if(transition_duration === undefined){
    transition_duration = 0
  }

  var no_players = _.reduce(players, function(memo, player){return memo && player===''}, true)
  d3.select('.prompt_text text').transition().duration(transition_duration).style('opacity', no_players ? 1 : 0)
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


function initial_players(){
  return [getParameterByName('player1'), getParameterByName('player2')]
}