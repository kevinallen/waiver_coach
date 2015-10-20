<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">

    <link href='https://fonts.googleapis.com/css?family=Play:400,700' rel='stylesheet' type='text/css'>
    <!-- still need to design an 32x32 icon -->
    <link rel="icon" href="favicon.ico">

    <title>Waiver Coach</title>

    <!-- Bootstrap core CSS -->
    <link href="css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="css/dashboard.css" rel="stylesheet">

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>
    <?php
    class Player {
        public $name = "";
        public $team = "";
        public $team_abbr = "";
        public $position = "";
        public $id;
    }

    $player1 = new Player();
    $player1->id = 1;
    $player1->name = "Charles Clay";
    $player1->team = "Buffalo Bills";
    $player1->team_abbr = "BUF";
    $player1->position = "Tight End";
    $player1->position_abbr = "TE";

    $player2 = new Player();
    $player2->id = 2;
    $player2->name = "Gary Barnidge";
    $player2->team = "Cleveland Browns";
    $player2->team_abbr = "CLE";
    $player2->position = "Tight End";
    $player2->position_abbr = "TE";

    $player3 = new Player();
    $player3->id = 3;
    $player3->name = "Kamar Aiken";
    $player3->team = "Baltimore Ravens";
    $player3->team_abbr = "BAL";
    $player3->position = "Wide Receiver";
    $player3->position_abbr = "WR";

    $player4 = new Player();
    $player4->id = 4;
    $player4->name = "LeGarrette Blount";
    $player4->team = "New England Patriots";
    $player4->team_abbr = "NE";
    $player4->position = "Running Back";
    $player4->position_abbr = "RB";

    $players = array($player1->id=>$player1,
                     $player2->id=>$player2,
                     $player3->id=>$player3,
                     $player4->id=>$player4);
    ?>
    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid title_bg">
        <div class="navbar-header ">
          <a class="navbar-brand title" href="#">Waiver Coach</a>
        </div>
        <!--
        <div id="navbar" class="navbar-collapse collapse">
          <ul class="nav navbar-nav navbar-right">
            <li><a href="#">Dashboard</a></li>
            <li><a href="#">Settings</a></li>
            <li><a href="#">Profile</a></li>
            <li><a href="#">Help</a></li>
          </ul>
          <form class="navbar-form navbar-right">
            <input type="text" class="form-control" placeholder="Search...">
          </form>
        </div>
            -->
      </div>
    </nav>

    <div class="container-fluid">
      <div class="row">
        <div class="col-sm-3 col-md-2 sidebar">
          <div class="nav-heading">
              Recommended
          </div>
          <ul class="nav nav-sidebar">
            <?php foreach($players as $player) :?>
                <li><a href="http://localhost:8080/?player=<?php echo $player->id?>"><?php echo $player->name;?></a></li>
            <?php endforeach;?>
          </ul>
        </div>
        <div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
          <h2 class="page-header">
              <?php if (array_key_exists('player',$_GET)) {
                  echo $players[$_GET['player']]->name;
              } else {
                  echo "Welcome to Waiver Coach";
              }
              ?>
          </h2>


          </div>
        </div>
      </div>
    </div>

    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
  </body>
</html>
