=head1 NAME
# Regroupez les annotations de l'étalon-or avec les prévisions. Générer des fichiers TSV.
# il faut que les fichiers sont rangés dans les dossiers intitulés Gold_X et Predictions_X.
# Par example:
#input_dossier
#├── Predictions_LVP
#|   └── Predictions_chapitre1.bios.tsv
#└── Gold_LVP
#    └── Gold_chapitre1.bios.tsv
# usage: 'perl comparer-gold-et-predictions.pl input_dossier'
# TSV format: TOKEN	PREDICTION	GOLD	VALIDITY
#				de		O		O		1
=cut
use strict;
use warnings;
use utf8;
use Getopt::Long;
use Pod::Usage;
use Unicode::Normalize;

my $help = 0;
my $predictions = "evaluation/L3i_NERC-EL/LVP";
my $gold = "corpus-annotations-golds/Gold_LVP";
my $skip_verification = 0;
my $outdir = "";

GetOptions(
	'help'        	=> \$help,
	'predictions=s' 	=> \$predictions,
	'gold=s'		  	=> \$gold,
	'results=s'		=> \$outdir
	);

my @files;


my @gold_files = glob("$gold/*.bios.tsv");
my @prediction_files = glob("$predictions/*.bios.tsv");


if ($#gold_files != $#prediction_files) {

	print STDERR "The number of *.bios.tsv files in the two folders does not match.";
	exit;

}

foreach my $i (0..$#gold_files) {
	# save the name of the actual file only
	$gold_files[$i] =~ /\/(.+?).bios.tsv/;
	my $work = $1;
	


    # create four arrays in parallel for the four columns
    my @words; # holds the token from the corpus
    my @gold_tags; # holds the gold-standard tags
    my @auto_tags; # holds automatically-generated tags
    my @validity;   # marks validity of generated tags with a 1 or 0
    
    open my $g, "<:utf8", "$gold_files[$i]" or die $!;

    print "$gold_files[$i]\n";

    while (<$g>) {
        
        chomp;
        next if $_ =~ /^TOKEN/;
		next if $_ eq "";
        my ($word, $gold_tag) = split("\t", $_);

        next unless $word;
        
        $gold_tag =~ s/
//;

        push (@gold_tags, $gold_tag);
        
        push (@words, $word);
    
    }
    
    
    open my $p, "<:utf8", "$prediction_files[$i]" or die $!;
	my $iteration = 0;
    while (<$p>) {
    	next if $_ eq "
";
        chomp;
        next if $_ =~ /^TOKEN/;        
        next if $_ eq "";

        
        my @line = split("\t", $_);

        my $electric_tag = $line[1];
        
        push(@auto_tags, $electric_tag);
    
    }
    SPLICE:
    for (0..$#auto_tags) {
	    unless (defined($auto_tags[$_])) {
	    	splice (@auto_tags, $_, 1);
	    	goto SPLICE;
	    }
    }
    GOLD:
    for (0..$#gold_tags) {
	    unless (defined($gold_tags[$_])) {
	    	splice (@gold_tags, $_, 1);
	    	goto GOLD;
	    }
    }
    unless ($#auto_tags == $#gold_tags) {
		print STDERR "The number of predicted tags is $#auto_tags but the number of gold tags is $#gold_tags\n";
		exit;
	}
    for my $p (0..$#gold_tags) {
        
        my $validity;
        $auto_tags[$p] = uc ($auto_tags[$p]);
        $gold_tags[$p] = uc ($gold_tags[$p]);
        $auto_tags[$p] =~ s/-PERS/-PER/;
        $gold_tags[$p] =~ s///;        
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
    
    my $outfile;
    if ($outdir eq "") {
    	$outfile = $prediction_files[$i];
	    $outfile =~ s/\.bios.tsv$/.predictions_vs_gold.tsv/;

    }
    else {
    	$prediction_files[$i] =~ /.+\/(.+?)\.bios.tsv$/;
    	$outfile = $1;
    	$outfile =~ s/Gold_//;
    	$outfile = "$outdir/$outfile.predictions_vs_gold.tsv";
    
    }
    print "$outfile\n";    

    open my $out, ">:utf8", $outfile or die $!;
    print $out "TOKEN\tPREDICTION\tGOLD\tVALIDITY\n";
	chomp @gold_tags;

    print scalar(@words) . "\n";
    print scalar(@auto_tags) . "\n";
    print scalar(@gold_tags) . "\n";        
    print scalar(@validity) . "\n";     
    for my $counter (0..$#words) {
        my $line =  "$words[$counter]\t$auto_tags[$counter]\t$gold_tags[$counter]\t$validity[$counter]\n";
        print $out $line;
    }
	

}