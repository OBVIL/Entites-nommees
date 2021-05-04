# Converts brat format files (.ann and .txt) to bios (tab-separated).
# Brat format notes: the first thing after the T1/A1, etc. is a tag type.
# The second thing is separated by one space, and it's the beginning of the string.
# Third comes the end of the string. Locations are expressed in the number of characters
# from the beginning of the file, where the count begins at zero.
# Three major tasks: 1. Translate the tags from French words like 'Lieu' to standard codes.
# 2. Tokenize the sentences and correlate with spans in the txt file.
# 3. Make sure that tags spanning multiple tokens are applied to all relevant tokens.

=head1 NAME

transformer-brat-a-bios.pl - convertir les fichiers .ann à format .bios.tsv

=head1 SYNOPSIS

transformer-brat-a-bios.pl [options] FILES

=head1 DESCRIPTION

Indexes additional feature sets for texts in the Tesserae corpus. To be run after
add_column.pl. By default, it adds the stem featureset for every text specified;
alternate featuresets can be selected using the --feature option.

=head1 OPTIONS AND ARGUMENTS

=over

=item I<FILES>

La liste des fichiers à transformer.

=item B<--replace>

Remplacer le fichier utilisé pour l'évaluation des annotations automatisées. A utiliser avec précaution.

=item B<--debug>

Imprimer des messages de débogage et de progression.

=item B<--help>

Imprimer l'utilisation et quitter.

=cut

#use warnings;
use strict;
use utf8;
use Data::Dumper;
use Scalar::Util qw(looks_like_number);
# get all the files, with filenames stripped off
my %filenames;
my %outnames;

use Getopt::Long;
use Pod::Usage;

my $debug = 0;
my $filepath;
my $help = 0;
my $replace = 0;

GetOptions(
	'help'            => \$help,
	'debug'           => \$debug,
);

	
if ($help) {

	pod2usage(1);
}


foreach my $file (@ARGV) {
	next if $file =~ /bios/;
	next unless $file =~ /\.ann$|\.txt$/;
	$file =~ s/\.\w\w\w$//;
	#find the 'predictions' file for the current text
	my $pred_file = $file;
	$pred_file =~ s/corpus-annotations-golds\/Gold_(.+)/evaluation\/L3i_NERC-EL\/comparer-predictions-et-gold\/Predictions_$1/;
	my $out_file = $pred_file;
	$pred_file =~ s/Gold_/Predictions_/;
	$out_file =~ s/Predictions_/Gold_/;

	$filenames{$file} = $pred_file;
	$outnames{$file} = $out_file;
}
if ($debug) {
	print Dumper %filenames;
	print Dumper %outnames;
	my $useless = <STDIN>;
}
foreach my $file (keys %filenames) {
	print "Reading $file.ann...";
	open my $ann, "<:utf8", "$file.ann", or die $!;
	open my $txt, "<:utf8", "$file.txt", or die $!;
	open my $pre, "<:utf8", "$filenames{$file}.bios.tsv", or die $!;

	my @tokens;
	my @tags; # list of tuples with the tag, beginning, and ending char offsets
	my @fulltext; # array that should contain all characters in the text file
	my $offset = 0;
	my %tokhash;
	my @pre_toks; #list of the tokens as parsed by the stanze tokenizer

	# read the .bios comparison file
	while (<$pre>) {
	
		my ($tok, $tag) = split("\t", $_);
		next if $tok eq "TOKEN";	
		push (@pre_toks, $tok);
	
	}

	# read the .ann file and find the elements that should have tags
	while (<$ann>) {
		
		# the line has three basic parts. The middle part comprises 3 things.
		my @line = split ("\t", $_);
		if ($line[0] =~ /^T/) {
			# if the line has a ; in it, it means that there are two ranges, 
			# marked separately by the user. To accomodate this improper tagging,
			# simply delete the separation.
			$line[1] =~ s/\d+\;\d+//;
			
			
			# make an array (tuple) of the three important things and add it to the list.
			my @tag = split(" ", $line[1]);
			push (@tags, \@tag);

		}				
	
	}

	while (<$txt>) {
		# error remaining: 
		next unless length $_ > 0;
		my $sentence = $_;
		my @line = split /([Qq]uelqu[’']un|[Gg]rand['’]peine|\s+|\w\w?['’]|[AE]h!|\!|\.\.\.|:|[,;.!?…]+|[Jj]usqu['’]|[Ll]orsqu['’]|[Aa]ujourd['’]hui|-on\W|-t[^a-zA-Z0-9\-êîàéá]|-elle\W|-ce\W|-tu\W|-là\W|-vous\W|-moi\W|-il\W)/, $_;
		
		# split the -tu\W into two constituent entries in the array and splice it in
		# first, find the indexes of all @line entries with these compounds
#		my @compounds = grep { $line[$_] =~ /-on\W|-t|-elle\W|-ce\W|-tu\W|-là\W|-vous\W|-moi\W|-il\W/ } 0 .. $#line;
		my @compounds = grep { $line[$_] =~ /-on\W|-t|-elle\W|-ce\W|-tu\W|-l\p{L}+\W|-vous\W|-moi\W|-il\W/ } 0 .. $#line;
		
		if ($sentence =~ /-t-/) {
			if ($debug) {		
				print join ("|", @line);
			}
#			my $useless = <STDIN>;
			
		
		}
		
		if (scalar @compounds > 0) {
			
			my $indexoffset = 0;
			# go through @line and split it at each place with a compound.
			foreach my $index (@compounds) {
				# if we have been through this loop before, then @line has expanded.
				# adjust the index accordingly.
				my $trueindex = $index + $indexoffset;							
				my ($empty, $pronoun, $punctuation) = split(/(-\p{L}+)/, $line[$trueindex]);
				#usually, $empty has nothing in it. But when the compound is -t-,
				# $empty contains the preceeding word. This is because the split only happened once.
				# the simple solution is to include $empty, and let it be cropped out later.
				splice (@line, $trueindex, 1, $empty, $pronoun, $punctuation);
				$indexoffset++;
			
			}
		
		}
		
			if ($sentence =~ /-t-/) {
				if ($debug) {
					print join ("|", @line);
				}
#			my $useless = <STDIN>;
			
		
		}
	
		
		# delete the empty @line entries
		my $indexoffset = 0;
		#There are uninitialized values in @line. How?
		my @empties = grep {$line[$_] eq ""} 0..$#line;
		foreach my $index (@empties) {
			
			my $trueindex = $index - $indexoffset;		
			splice (@line, $trueindex, 1);
			$indexoffset++;
		
		}
		
		#check for broken elipses
		#reset $indexoffset because we're going to modify the array again
		$indexoffset = 0;
		my @busted_elipses = grep {$line[$_] =~ /^\.\.+$/ } 0..$#line;
		if (scalar @busted_elipses > 0) {
		if ($debug) {print Dumper @busted_elipses;}

			for my $i (0..$#busted_elipses) {
				#if the token before is just a period...
				if ($line[$busted_elipses[$i]- 1 -$indexoffset] =~ /^\.+$/) {
					#the place to edit is the first set of periods.
					my $index = $busted_elipses[$i] - 1 - $indexoffset;
			
					my $replacement = $line[$index] . $line[$index + 1];
					#merge the two and add to the offset
					splice (@line, $index, 2, $replacement);

					$indexoffset++;
				
				}
		
			}
		}
		#check for broken elipses going the OTHER direction.
		#reset $indexoffset because we're going to modify the array again
		$indexoffset = 0;
		@busted_elipses = grep {$line[$_] =~ /^\.\.+$|^!$/ } 0..$#line;
		if (scalar @busted_elipses > 0) {
		if ($debug) {print Dumper @busted_elipses;}

			for my $i (0..$#busted_elipses) {
				#if the token after is just a period...
				if ($line[$busted_elipses[$i] + 1 - $indexoffset] =~ /^\.+$/) {
					#the place to edit is the first set of periods.
					my $index = $busted_elipses[$i] - $indexoffset;
			
					my $replacement = $line[$index] . $line[$index + 1];
					#merge the two and add to the offset
					splice (@line, $index, 2, $replacement);

					$indexoffset++;
				
				}
			}
		}
		
		#do it again for -t-elle, etc. At this point, this should really be a function call.
		$indexoffset = 0;
		@busted_elipses = grep {$line[$_] =~ /^-$/ } 0..$#line;
		if (scalar @busted_elipses > 0) {
		if ($debug) {print Dumper @busted_elipses;}

			for my $i (0..$#busted_elipses) {
				#if the token after is just a period...
				if ($line[$busted_elipses[$i] + 1 - $indexoffset] =~ /^on|elles?|il$/ && $line[$busted_elipses[$i] - 1 - $indexoffset] eq "-t") {
					#the place to edit is the first set of periods.
					my $index = $busted_elipses[$i] - $indexoffset;
			
					my $replacement = $line[$index] . $line[$index + 1];
					#merge the two and add to the offset
					splice (@line, $index, 2, $replacement);

					$indexoffset++;
				
				}
			}
		}
		
		if ($sentence =~ /-t-/) {
		
			if ($debug) {print join ("|", @line);}
#			my $useless = <STDIN>;
			
		
		}		
		
		# build a hash of hashes. First hash keyed by position in text file.
		foreach my $token (@line) {


			# the offset must be the key for the new tokens
			my %temp = (
				'STRING' => $token,
				'END' => $offset + length($token),
				'TAG' => 'O'
			);
		
			$tokhash{$offset} = \%temp;
		
			$offset = $offset + length($token);
		
		}

		push(@fulltext, @line);
		# this needs to come later, after token length sums are used to find the span.
		LINE:
		for my $n (0..$#line) {		
			if ($line[$n] =~ /^\s+/ or $line[$n] eq "") { #23629
			
				splice (@line, $n, 1);
				goto LINE;
			}
		}

		push(@tokens, @line);
	
	}

	my %lookup = (
		'Lieu' => 'LOC',
		'Personnage' => 'PER',
		'Misc' => 'MISC'
	);
	my %errors;

	my @token_begins = sort {$a <=> $b} keys %tokhash;

	foreach my $ref (@tags) {
	
		my ($tag, $begin, $end) = @{$ref};


		# the beginning of a string should get the B- prefix.
		# But if the span of the .ann tag is longer, one of two things should happen
		# 1. the next token is still within the .ann tag span, so give it the I- tag
		# 2. the .ann span ends at the exact same place as the next token, so give it E-
		if ($tokhash{$begin}->{'END'} == $end) {
		
			$tokhash{$begin}->{'TAG'} = "S-$lookup{$tag}";
		
		}
		else {		

			$tokhash{$begin}->{'TAG'} = "B-$lookup{$tag}";
		
			# look in the array of token beginnings for the current beginning's address
#			my $index = first { $token_begins[$_] eq "$begin" } 0..$#token_begins;
			my @i = grep { $token_begins[$_] == $begin } 0 .. $#token_begins;
			my $index = $i[0];

			# add one to that address, so that we can look at the next token
			$index++;

			#keep going until the end of the token is past the end of the .ann span
			#could be done with the beginning too...

			while ($tokhash{$token_begins[$index]}->{'END'} <= $end) {
			
				if ($tokhash{$token_begins[$index]}->{'END'} < $end) {
			
					$tokhash{$token_begins[$index]}->{'TAG'} = "I-$lookup{$tag}";
			
				}
				elsif ($tokhash{$token_begins[$index]}->{'END'} == $end) {
			
					$tokhash{$token_begins[$index]}->{'TAG'} = "E-$lookup{$tag}";
			
				}
				$index++;
			}

		
		}

	
	}
	my $out;
	if ($replace) {
		open $out, ">:utf8", "$outnames{$file}.bios.tsv", or die $!;
	}
	else {
		open $out, ">:utf8", "$file.bios.tsv" or die $!;
	}
	foreach my $key (sort {$a <=> $b} keys %tokhash) {
	
		if ($tokhash{$key}->{'STRING'} =~ /^\s+/ or $tokhash{$key}->{'STRING'} eq "") {
		
			delete($tokhash{$key});
			
		}
	}

	# error handling
	# expect two types of errors: 
	# incorrect splits of tokens that a. should be merged or b. must be split
	# AND \n characters in the stanza file that have no correlated \n in the new hash
	TOKEN:
	my @token_offsets = sort {$a <=> $b} keys %tokhash;
	
	for my $i (0..$#token_offsets) {
		
		if ($tokhash{$token_offsets[$i]}->{'STRING'} ne $pre_toks[$i]) {

				if ($pre_toks[$i] eq "\n") {
					if ($debug) {
					print "The current token, '$tokhash{$token_offsets[$i]}->{'STRING'}', ";
					print "is not matching an expected newline character.";
					print "Attempting repair by inserting a newline.\n--------------------------\n";		
					
				# are newline characters tokens, as far as the offset # is concerned?
				# does it matter?
				# we need to insert a \n after the previous offset and before the next.
				print "$token_offsets[$i - 1]->";
				print Dumper $tokhash{$token_offsets[$i - 1]};
				print "$token_offsets[$i]->";
				print Dumper $tokhash{$token_offsets[$i]};
				print "$token_offsets[$i + 1]->";
				print Dumper $tokhash{$token_offsets[$i + 1]};		}
				# to avoid overwriting the next hash, while ensuring we are past the current,
				# use the previous 'END' entry as the offset for the hash representing the \n charcacter.
				# or we could use the current offset minus 1.

				# sometimes, when the hash has already been modified, the previous offset is taken.
				# So to make sure that the previous entry isn't overwritten, use a floating point.
				my $new_offset = $token_offsets[$i] - .5;

				my %temp = (
					'STRING' => "\n",
					'END' => $new_offset + 1,
					'TAG' => "O"
				);			
				$tokhash{$new_offset} = \%temp;
				goto TOKEN;
			
		}

			
			#try merging;
			if ($tokhash{$token_offsets[$i + 1]}) {
				# check whether merging with the next one or two tokens would match the stanza file
				my $merged = $tokhash{$token_offsets[$i]}->{'STRING'} . $tokhash{$token_offsets[$i + 1]}->{'STRING'};
				my $double_merged = $merged . $tokhash{$token_offsets[$i + 2]}->{'STRING'};			
				
				# try merging but also cutting off the string that comes next in stanza (usually punctuation)
				my $split_and_merged = $merged;
				my $thirdstring = $pre_toks[$i + 1];
				if ($thirdstring ne "") {
					$split_and_merged =~ s/\Q$thirdstring\E$//;
				}			
				if ($merged eq $pre_toks[$i]) {
					if ($debug) {
					print "The current token, '$tokhash{$token_offsets[$i]}->{'STRING'}', ";
					print "can be merged with the next token, '$tokhash{$token_offsets[$i + 1]}->{'STRING'}' ";
					print "to match '$pre_toks[$i]'. Attempting repair by merging.\n--------------------------\n";
					}
					# replace the string in the current $tokhash entry
					$tokhash{$token_offsets[$i]}->{'STRING'} = $merged;
					# update the ending variable
					$tokhash{$token_offsets[$i]}->{'END'} = length($merged) + $token_offsets[$i];
					#delete the next (redundant) entry in the hash
					delete($tokhash{$token_offsets[$i + 1]});
					goto TOKEN;
				}
				elsif ($double_merged eq $pre_toks[$i]) {
					if ($debug) {
					print "The current token, '$tokhash{$token_offsets[$i]}->{'STRING'}', ";
					print "can be merged with the next two tokens, '$tokhash{$token_offsets[$i + 1]}->{'STRING'}' ";
					print "and '$tokhash{$token_offsets[$i + 2]}->{'STRING'}' ";
					print "to match '$pre_toks[$i]'. Attempting repair by merging.\n--------------------------\n";
					}
					# replace the string in the current $tokhash entry
					$tokhash{$token_offsets[$i]}->{'STRING'} = $double_merged;
					# update the ending variable
					$tokhash{$token_offsets[$i]}->{'END'} = length($double_merged) + $token_offsets[$i];
					#delete the next (redundant) entry in the hash
					delete($tokhash{$token_offsets[$i + 1]});
					delete($tokhash{$token_offsets[$i + 2]});
					goto TOKEN;
				}
				elsif ($thirdstring ne "" && $split_and_merged eq $pre_toks[$i]) {
				
					# replace the string in the current $tokhash entry
					$tokhash{$token_offsets[$i]}->{'STRING'} = $split_and_merged;
					# update the ending variable
					$tokhash{$token_offsets[$i]}->{'END'} = length($split_and_merged) + $token_offsets[$i];
					#change the next entry in the hash to the punctuation that was split off
					$tokhash{$token_offsets[$i + 1]}->{'STRING'} = $thirdstring;
					# update the ending variable
					$tokhash{$token_offsets[$i + 1]}->{'END'} = length($thirdstring) + $token_offsets[$i + 1];
					goto TOKEN;
				
				}
			}
			#try splitting
			
			# use the current stanza token as the part to break off
			# this assumes that the problem is that the token wasn't split correctly.
			my $splitter = $pre_toks[$i];
			# \Q to \E makes any special characters function like normal characters.
			my @tokens = split /(\Q$splitter\E)/, $tokhash{$token_offsets[$i]}->{'STRING'};
			if ($tokens[1]) {
				if ($tokens[1] eq $pre_toks[$i]) {
					if ($debug) {
					print "The current token, '$tokhash{$token_offsets[$i]}->{'STRING'}', ";
					print "can be split by the current token in the stanza list, '$splitter'.";
					print "Attempting repair by splitting.\n--------------------------\n";
					print "$tokhash{$token_offsets[$i]}->{'STRING'}| \t |$pre_toks[$i]|\n";

					print "$token_offsets[$i]->";
					print Dumper $tokhash{$token_offsets[$i]};
					print "$token_offsets[$i+1]->";
					print Dumper $tokhash{$token_offsets[$i+1]};
					print "==========MODIFICATIONS BELOW===========\n";	}
					# take the current string and split it.
					# then subtract the length of the second of two strings from the ending offset
					# this gives the new ending offset.
					# the location of the new hash should be 1 plus the new ending offset
					# this should be before the next already-occuring hash


					$tokhash{$token_offsets[$i]}->{'STRING'} = $tokens[1];
					$tokhash{$token_offsets[$i]}->{'END'} -= length($tokens[2]);
				
					# now create a new entry for the second part of the split string
					my $new_offset = $tokhash{$token_offsets[$i]}->{'END'} + 1;
					# initialize entry with the same tag as the unsplit version
					my %temp = (
						'STRING' => $tokens[2],
						'END' => $new_offset + length($tokens[2]),
						'TAG' => $tokhash{$token_offsets[$i]}->{'TAG'}
					);
					# if the splitter is just a single space, drop it.
					# otherwise, make a new hash entry for it.
					unless ($tokens[2] eq " ") {
						$tokhash{$new_offset} = \%temp;
					}
					if ($debug) {
					print "$token_offsets[$i]->";
					print Dumper $tokhash{$token_offsets[$i]};
					print "$new_offset->";
					print Dumper $tokhash{$new_offset};	}
					goto TOKEN;
				
					#change the string value inside the hash for this token offset
			
				}
			}
			#this is triggered when the script encounters an unexpected error.
			print "Unable to repair inconsitency. Token '0' below represents the current token.\n";
			print "\tOFFSET|\tTOKENIZATION\t STANZA TOKENIZATION\n";
			print "-3:\t $token_offsets[$i -3]|$tokhash{$token_offsets[$i -3]}->{'STRING'}| \t\t |$pre_toks[$i-3]|\n";
			print "-2:\t $token_offsets[$i -2]|$tokhash{$token_offsets[$i -2]}->{'STRING'}| \t\t |$pre_toks[$i-2]|\n";			
			print "-1:\t $token_offsets[$i -1]|$tokhash{$token_offsets[$i -1]}->{'STRING'}| \t\t |$pre_toks[$i-1]|\n";
			print "0:\t $token_offsets[$i]|$tokhash{$token_offsets[$i]}->{'STRING'}| \t\t |$pre_toks[$i]|\n";
			print "+1:\t $token_offsets[$i +1]|$tokhash{$token_offsets[$i + 1]}->{'STRING'}| \t\t |$pre_toks[$i+1]|\n";
			print "+2:\t $token_offsets[$i +2]|$tokhash{$token_offsets[$i + 2]}->{'STRING'}| \t\t |$pre_toks[$i+2]|\n";
			print "Try restarting with --debug to locate the problem, or press enter to continue.\n";
			my $useless = <STDIN>;
		
		}
	
	}
	my $final;
	foreach my $key (sort {$a <=> $b} keys %tokhash) {
		if ("$tokhash{$key}->{'STRING'}" eq "\n") {
		
			$final .= "\n";
		
		}
		else {
			$final .= "$tokhash{$key}->{'STRING'}" . "\t" . $tokhash{$key}->{'TAG'} . "\n";

		}
	}
	
	$final =~ s/^\tO\n//g;
	$final =~ s/\n\n/\n\t\n/g;
	
	print $out $final;

	
}