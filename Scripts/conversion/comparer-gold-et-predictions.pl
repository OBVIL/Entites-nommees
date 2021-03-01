# Regroupez les annotations de l'étalon-or avec les prévisions. Générer des fichiers TSV.
# il faut que les fichiers sont rangés dans les dossiers intitulés Gold_X et Predictions_X.
# Par example:
#input_dossier
#├── Predictions_LVP
#|   └── Predictions_chapitre1.bios.tsv
#└── Gold_LVP
#    └── Gold_chapitre1.bios.tsv
# usage: 'perl stitch.pl input_dossier'
# TSV format: TOKEN	PREDICTION	GOLD	VALIDITY
#				de		O		O		1

use strict;
use warnings;


my @files = glob("$ARGV[0]/*");

foreach (@ARGV) {
	# go through all the files in * from the command line
	# skip if the current path is not a file
	next if -f;
	
	# remove the enclosing folder from the filepath
	$_ =~ /(Gold_|Predictions_)(.+)/;
	# save the name of the actual file only
	my $work = $2;
	# construct a filepath to store the stiched tsv table
	my @golds = <"Gold_$work/*">;
	
	for my $gold (@golds) {
		# create four arrays in parallel for the four columns
		my @words; # holds the token from the corpus
		my @gold_tags; # holds the gold-standard tags
		my @auto_tags; # holds automatically-generated tags
		my @validity;	# marks validity of generated tags with a 1 or 0
		
		open my $g, "<:utf8", "$gold" or die $!;
	
		print "$gold\n";
		
		while (<$g>) {
			
			chomp;

			my ($word, $gold_tag) = split("\t", $_);

			next unless $word;
			
			$gold_tag =~ s///;

			push (@gold_tags, $gold_tag);
			
			push (@words, $word);
		
		}
		
		my $prediction = $gold;
		
		$prediction =~ s/Gold_/Predictions_/g;
		print "$prediction\n";
		open my $p, "<:utf8", "$prediction" or die $!;

		while (<$p>) {
		
			chomp;
			
			next if $_ eq "";
			
			my @line = split("\t", $_);
			
			my $electric_tag = $line[1];
			
			push(@auto_tags, $electric_tag);
		
		}
				
		for my $p (0..$#gold_tags) {
		
		my $validity;
		
		# the check for validity is complicated.
		# it is necessary to accomodate different spellings, but only for tags
		# the empty tag 'O' requires an exact match
		if (length($auto_tags[$p]) > 1 && length($gold_tags[$p]) > 1) {
		
			if ($auto_tags[$p] =~ /$gold_tags[$p]/i | $gold_tags[$p] =~ $auto_tags[$p]) {
				$validity = 1;
			}
			else {
				$validity = 0;
			}
		}
		else {
			if ($auto_tags[$p] =~ /$gold_tags[$p]/i && $gold_tags[$p] =~ $auto_tags[$p]) {
				$validity = 1;
			}
			else {
				$validity = 0;
			}
		}
			
			push (@validity, $validity);
		}
		
		my $outfile = $prediction;
		
		$outfile =~ s/.+\/Predictions_//;
		
		$outfile = "Predictions_vs_Gold_$work/TSV_" . $outfile;
		
		print "$outfile\n";
		
		open my $out, ">:utf8", $outfile or die $!;

		print $out "TOKEN\tNE-COARSE-LIT\tGOLD\tVALIDITY\n";


		print scalar(@words) . "\n";
		print scalar(@auto_tags) . "\n";
		print scalar(@gold_tags) . "\n";		
		print scalar(@validity) . "\n";		
		my $useless = <STDIN>;

		for my $counter (0..$#words) {
			print $out "$words[$counter]\t$auto_tags[$counter]\t$gold_tags[$counter]\t$validity[$counter]\n";
		}
	}

}