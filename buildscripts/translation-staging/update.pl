#!/usr/bin/perl

$download="/export/download";
$basename="for_use_makehuman_v1-0_english_";
$hglangdir="../../makehuman/data/languages";

# Comment out the following line to skip this step
$upload="makehuman\@192.168.11.5:~/www.makehuman.org/sites/default/root/shared/lang";

# --- END CONFIGURATION ---


use Locale::Language;

open(FILES,"find $download -name \"$basename*.json\" |") || die "Urrk\n";

system "mkdir -p html";
system "mkdir -p diff";
system "mkdir -p lang";

system "rm -f html/*.html";
system "rm -f diff/*.diff";
system "rm -f lang/*.json";

$file{"index.html"} = "unknown";

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

  $file{"$fn.html"} = $code;

  print HTML "<!DOCTYPE html>\n<html lang=\"$code\">\n<head>\n";
  print HTML "<meta charset=\"utf-8\">\n";
  print HTML "<title>$fn</title>\n";
  print HTML "<style>\n";
  print HTML ".orig { display: block; width: 100%; background-color: #FFFFAA; margin: 5px; }\n";
  print HTML ".trans { display: block; width: 100%; background-color: #BBBBFF; margin: 5px; margin-bottom: 20px; }\n";
  print HTML "</style>\n";
  print HTML "</head>\n<body>\n";
  
  while($line = <LANG>)
  {
    if($line =~ m/\"([^"]+)\".*:.*\"([^"]+)\"/)
    {
      print HTML "<b lang=\"en\">$1</b><br />\n$2<br /><br />\n"; 
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

$part0='https://translate.google.com/translate?sl=';
$part1='&tl=en&js=y&prev=_t&hl=en&ie=UTF-8&u=http%3A%2F%2Fwww.makehuman.org%2Fshared%2Flang%2F';
$part2='&edit-text=&act=url';

chdir("html");
open(PIPE,"find . -name \"*.html\" |") || die;
open(LINKS,">links.html") || die;
print LINKS "<html><body><table border=\"1\" cellpadding=\"3\">\n";
print LINKS "<tr><td><b>Raw</b></td><td><b>Google translate</b></td></tr>\n";
while($inlin = <PIPE>)
{
  chomp($inlin);
  $inlin =~ s/\.html//g;
  $inlin =~ s/[^a-z]+//g;
  $code = $file{"$inlin.html"};
  print LINKS "<tr><td><a href=\"$inlin.html\">$inlin</a></td>";
  print LINKS "<td><a href=\"";
  print LINKS $part0;
  print LINKS $code;
  print LINKS $part1;
  print LINKS "$inlin.html";
  print LINKS $part2;
  
  print LINKS "\">$inlin</a></td></tr>\n";
}
close(PIPE);
print LINKS "</table>\n";
print LINKS "<br /><br />";
print LINKS "<a href=\"lang.zip\">Download zip with language files</a> (unzip in makehuman/data/languages and restart makehuman)<br /><br />\n";
print LINKS "</body></html>\n";

system "scp links.html $upload";

chdir("../lang");

system "rm -f lang.zip";
system "zip lang.zip *.json";
system "scp lang.zip $upload";

