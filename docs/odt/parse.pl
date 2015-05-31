#!/usr/bin/perl

use File::Basename;

system "rm -f unescaped.xml docexport.xml";
system "wget http://www.makehuman.org/docexport.xml";

open(FIL,"docexport.xml") || die;
open(UT,">unescaped.xml") || die;

if(!-e "data") { mkdir "data"; }

$pxcmratio = "50";

$isinpre = 0;

while($inlin = <FIL>)
{
  $inlin =~ s/\<\!\[CDATA\[//g;
  $inlin =~ s/\]\]\>//g;
  $inlin =~ s/ +/ /g;
  $inlin =~ s/ \< / &lt; /g;
  $inlin =~ s/ \<0/ &lt;0/g;
  $inlin =~ s/\> +/>/g;
  $inlin =~ s/ +\</</g;
  $inlin =~ s/^ +//g;
  $inlin =~ s/ alt="[^"]*"//g;
  $inlin =~ s/<a href="([^"]*)">\s*<img src="([^"]*)"/<a href="$1"><img src="$1"/g;
  $inlin =~ s/src="http:\/\/www.makehuman.org/src="/g;
  $inlin =~ s/src="http:\/\/makehuman.org/src="/g;
  $inlin =~ s/\/sites\/mhnew.jwp.se\/files\///g;
  $inlin =~ s/\/sites\/makehuman.org\/files\///g;
  $inlin =~ s/\/sites\/www.makehuman.org\/files\///g;
  $inlin =~ s/"\/images\//"_images\//g;
  $inlin =~ s/ style="[^"]*"//g;
  $inlin =~ s/ class="[^"]*"//g;
  $inlin =~ s/ id="[^"]*"//g;
  $inlin =~ s/\<span[^>]*>//g;
  $inlin =~ s/\<\/span>//g;
  $inlin =~ s/\xc2\xa0/ /g;
  $inlin =~ s/\x09/<TAB\/>/g;
  $inlin =~ s/\<div\>//g;
  $inlin =~ s/\<\/div\>//g;
  #$inlin =~ s/\<pre\>/<pre>\n/g;
  #$inlin =~ s/\<\/pre\>/<pre>\n/g;

#  if($inlin =~ m/<pre>/)
#  {
#    $isinpre = 1;
#  }
#
#  if($isinpre)
#  {
#    $inlin =~ s/\<br \>/<BREAK\/>\n/g;
#    $inlin =~ s/[\x0a\x0d]/<BREAK\/>\n/g;
#    $inlin =~ s/ /<SPC\/>/g;
#  }
#
#  if($inlin =~ m/<\/pre>/)
#  {
#    $isinpre = 0;
#  }

  print UT $inlin;
}

close(UT);
close(FIL);

@volumes = (
"MakeHuman Manual"
);

system "rm -rf work";
mkdir "work";
mkdir "work/export";

system "xsltproc analyze.xsl unescaped.xml | sort | uniq > analyze.txt";

my(@added);

foreach $volume (@volumes)
{
  $fn = $volume;
  $fn =~ s/ //g;
  $fn =~ s/&//g;

  system "xsltproc --stringparam volume '$volume' preprocess.xsl unescaped.xml > work/$fn.xml";
  system "xsltproc imagelist.xsl work/$fn.xml > work/$fn.lst";

  system 'sed -i -e \'s/src="[^"]*\/\([^"]*\)"/src="Pictures\/\1"/g\' work/' . $fn . ".xml";
  
  open(NOIMG,"work/$fn.xml");
  open(HASIMG,">work/$fn-tmp.xml");
  open(IMG,"work/$fn.lst");
  open(GEOM,">work/$fn-geom.txt");

  while($inlin = <NOIMG>)
  {
    print HASIMG $inlin;

    if($inlin =~ m/<document>/)
    {
      print HASIMG "  <images>\n";
      while($img = <IMG>)
      {
        chomp($img);
        $geom = `identify -verbose data/$img | grep Geometry`;
        chomp($geom);
        $geom =~ m/(\d+)x(\d+).*/;
        $x = $1;
        $y = $2;
        $geom = "$x $y";
        $x = $x / $pxcmratio;
        $y = $y / $pxcmratio;
 
        $x = substr("" . $x, 0, 6);
        $y = substr("" . $y, 0, 6);

        $x .= "cm";
        $y .= "cm";

        my($filename, $directories, $suffix) = fileparse($img);  


        if($filename ~~ @added)
        {
          print "$filename was already added\n";
        }
        else
        {
          push(@added,$filename);
          print GEOM "$filename $geom $x $y\n";        
          print HASIMG "    <image file=\"Pictures/$filename\" width=\"$x\" height=\"$y\" />\n";
        }
      }
      print HASIMG "  </images>\n";
    }
  }

  close(GEOM);
  close(NOIMG);
  close(HASIMG);
  close(IMG);
  
  system "cp work/$fn-tmp.xml work/$fn-step.xml";
  system "uniq work/$fn-tmp.xml > work/$fn.xml";
}

foreach $volume (@volumes)
{
  $fn = $volume;
  $fn =~ s/ //g;
  $fn =~ s/&//g;

system "rm -rf work/doc";
system "cp -rf odt-template work/doc";

open(INFIL,"work/$fn.lst") || die;
open(UTFIL,">>work/doc/META-INF/manifest.xml") || die;

while($inlin = <INFIL>)
{
  chomp($inlin);
  my($filename, $directories, $suffix) = fileparse($inlin);  

  system "cp -f data/$inlin work/doc/Pictures";
  print UTFIL "  <manifest:file-entry manifest:media-type=\"image/png\" manifest:full-path=\"Pictures/$filename\"/>\n";
}

print UTFIL "</manifest:manifest>\n";

close(UTFIL);
close(INFIL);

system "xsltproc stylesheet.xsl work/$fn.xml > work/doc/content.xml";

chdir "work/doc";

system "rm -rf ../export/$fn.odt";

system "zip -r ../export/$fn.odt *";

chdir "../.."
}

open(ANA,">>analyze.txt");

foreach $volume (@volumes)
{
  $fn = $volume;
  $fn =~ s/ //g;
  $fn =~ s/&//g;

  open(GEOM,"work/$fn-geom.txt");

  print "work/$fn-geom.txt\n";

  while($inlin = <GEOM>)
  {
    chomp($inlin);
    ($img,$xp,$yp,$xc,$yx) = split(/ /,$inlin);
    if($xp > 600 || $yp > 800)
    {
      $xml = "xmllint --format --xpath \"//img[\@src='Pictures/" . $img . "']/ancestor::node/\@id\" work/" . $fn . ".xml";
      $xpath = `$xml`;

      $xpath =~ s/[^0-9]//g;

      print ANA "http://www.makehuman.org/node/$xpath image $img is too large ($xp" . "x$yp)\n";
    }
  }

  close(GEOM);
}
close(ANA);


