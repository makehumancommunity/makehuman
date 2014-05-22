#!/usr/bin/perl

$download="/export/download";
$basename="for_use_makehuman_v1-0_english_";
$hglangdir="../../makehuman/data/languages";

# Comment out the following line to skip this step
$upload="makehuman\@192.168.11.5:~/www.makehuman.org/sites/default/root/shared/lang";

# --- END CONFIGURATION ---


use Locale::Language;

$langmatch{"sv_SE"} = "swedish";
$langmatch{"zh_CN"} = "chinese";

open(FILES,"find $download -name \"$basename*.json\" |") || die "Urrk\n";

system "mkdir -p html";
system "mkdir -p diff";
system "mkdir -p lang";

system "rm -f html/*.html";
system "rm -f diff/*.diff";
system "rm -f lang/*.json";

while($inlin = <FILES>)
{
  $search = "$basename([^.]+).json";
  $inlin =~ m/$search/;
  chomp($inlin);
  $lang = $1;
  $lang =~ m/([a-z][a-z]).*/;
  $code = $1;
  $fn = lc(code2language($code)) || $lang;
  system "cp $inlin lang/$fn.json";
  if(-e "$hglangdir/$fn.json")
  {
    system "diff $hglangdir/$fn.json lang/$fn.json > diff/$fn.diff";
  }
  open(LANG,"lang/$fn.json") || die "Eeeek\n";
  open(HTML,">html/$fn.html") || die "Blerk\n";

  print HTML "<!DOCTYPE html>\n<html lang=\"$code\">\n<head>\n";
  print HTML "<meta charset=\"utf-8\">\n";
  print HTML "<title>$fn</title>\n";
  print HTML "</head>\n<body>\n";
  
  while($line = <LANG>)
  {
    if($line =~ m/\"([^"]+)\".*:.*\"([^"]+)\"/)
    {
      print HTML "<!-- $1 -->\n<p>$2</p>\n\n"; 
    }
  }
  close(HTML);
  close(LANG);

  if($upload)
  {
    system "scp html/$fn.html $upload";
  }
}

close(FILES);

$part1='https://translate.google.com/translate?sl=auto&tl=en&js=y&prev=_t&hl=en&ie=UTF-8&u=http%3A%2F%2Fwww.makehuman.org%2Fshared%2Flang%2F';
$part2='&edit-text=&act=url';

chdir("html");
open(PIPE,"find . -name \"*.html\" |") || die;
open(LINKS,">links.html") || die;
print LINKS "<html><body><table>\n";
print LINKS "<tr><td><b>Raw</b></td><td><b>Google translate</b></td></tr>\n";
while($inlin = <PIPE>)
{
  chomp($inlin);
  $inlin =~ s/\.html//g;
  $inlin =~ s/[^a-z]+//g;
  print LINKS "<tr><td><a href=\"$inlin.html\">$inlin</a></td>";
  print LINKS "<td><a href=\"";
  print LINKS $part1;
  print LINKS "$inlin.html";
  print LINKS $part2;
  
  print LINKS "\">$inlin</a></td></tr>\n";
}
close(PIPE);

print LINKS "</body></html>\n";

system "scp links.html $upload";

