#!/usr/bin/perl

use File::Basename;

sub parseLang()
{
  $file = shift;
  open(LANG, $file) || die "could not open $file\n\n";

  my(%json);
  my($line);

  while($line = <LANG>)
  {
    if($line =~ m/\"([^"]+)\".*:.*\"([^"]+)\"/)
    {
      $json{$1} = $2;
    }
  }

  return %json;
}

$sourceFile = $ARGV[0];
$langDir = $ARGV[1];

if(!$sourceFile) 
{
  $sourceFile = "next_planned_master_for_transifex.json";
}

if(!$langDir)
{
  $langDir = "../../makehuman/data/languages";
}

if(!$sourceFile || ! -e $sourceFile) 
{
  die "source file was not given or did not exist\n\n";
}

if(!$langDir || ! -e $langDir) 
{
  die "language directory was not given or did not exist\n\n";
}

my(%english) = &parseLang($sourceFile);

open(FILES,"find $langDir -name \"*.json\" | sort |") || die "Could not enumerate json files\n\n";

print "<br /><br />\n";
print "<h1>Overview of translation status</h1>\n";
print "<table border=\"1\">\n<tr><td><b>Language</b></td><td><b>Missing</b></td><td><b>Untranslated</b></td></tr>\n";

my(%langMiss);

while($inlin = <FILES>)
{
  chomp($inlin);
  ($lang,$path,$suffix) = fileparse($inlin,(".json"));

  print "<tr>\n";
  print "  <td>$lang</td>\n";

  my(%json) = &parseLang($inlin);

  $missing = 0;
  $untrans = 0;

  my(@mymissing) = ();

  foreach $engstr (keys(%english))
  {
    if(!$json{$engstr})
    {
      $missing++;
    }
    else
    {
      if($json{$engstr} eq $engstr)
      {
        push(@mymissing,$engstr);
        $untrans++;
      }
    }
  }

  print "  <td>$missing</td>\n"; 
  print "  <td>$untrans</td>\n"; 
  print "</tr>\n\n"; 

  $langMiss{$lang} = \@mymissing;
}

print "</table>\n";

close(FILES);

@langs = sort(keys(%langMiss));

print "<br /><h1>About untranslated strings</h1>\n";
print "<p>The following lists are untranslated strings per language. A string is considered untranslated if it is exactly the same as in the ";
print "english source file. The algorithm cannot separate this from strings which are in fact the same in both languages, so some are bogus.</p><br />\n";

foreach $lang (@langs)
{
  print "<br /><h1>Untranslated strings in $lang</h1>\n<ul>\n";
  my(@m) = sort(@{$langMiss{$lang}});
  foreach $l (@m)
  {
    print "<li>$l</li>\n";
  }
  print "</ul><br />\n\n";
}

