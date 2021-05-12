use warnings;

foreach $file (@ARGV) {

	open my $f, "<:utf8", $file or die $!;
	my $outfile = $file;
	$outfile =~ s/\.tsv/bios.tsv/;
	open my $o, ">:utf8", $outfile or die $!;

	my (@tokens, @tags);
	while (<$f>) {
		
		#skip everyting junky
		next unless $_ =~ /\t/;
		# only need the first two tabs
		my @line = split "\t", $_;
		
		$line[3] =~ s/\[.+\]//;
		push (@tokens, $line[2]);
		push (@tags, $line[3]);
	
	}

	#add the B-, I-, and E- tags
	my $previous = "";
	my $next = "";
	for my $i (0..$#tags) {
		#skip if there is no tag on this token
		next unless $tags[$i] ne "_";
		if ($i > 0) { 
			$previous = $tags[$i -1];
		}
		if ($i < $#tags) {
			$next = $tags[$i + 1];
		}
		# scenario: there is nothing before this tag
		if ($previous eq "_") {
			# and there is nothing after it
			if ($next eq "_") {
			
				$tags[$i] = "S-" . $tags[$i];
				next;
			
			}
			else {#or if there is someing after it, this is a beginning
			
				$tags[$i] = "B-" . $tags[$i];
				next;
			}
			
		}
		else { 
			if ($next eq "_") {# there is nothing after this tag
				# that means this is the end 
				$tags[$i] = "E-" . $tags[$i];
				next;
			}
			else { # there is something after this tag
				# this is an interior tag
				$tags[$i] = "I-" . $tags[$i];
				next;
			}
		}
		
	}
	#replace all underscores with Os
	grep { $tags[$_] =~ s/^_$/O/ } 0 .. $#tags;
	grep { $tags[$_] =~ s/PERS$/PER/ } 0 .. $#tags;
	
	for my $i (0..$#tags) {
	
		print $o "$tokens[$i]\t$tags[$i]\n";
	
	}
	
}