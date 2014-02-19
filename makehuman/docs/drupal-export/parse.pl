#!/usr/bin/perl

open(FIL,"docexport.xml") || die;
open(UT,">unescaped.xml") || die;

if(!-e "rst") { mkdir "rst"; }

while($inlin = <FIL>)
{
  $inlin =~ s/\&lt;/</g;
  $inlin =~ s/\&gt;/>/g;
  $inlin =~ s/\x09/ /g;
  $inlin =~ s/ +/ /g;
  $inlin =~ s/ \< / &lt; /g;
  $inlin =~ s/ \<0/ &lt;0/g;
  $inlin =~ s/\> +/>/g;
  $inlin =~ s/ +\</</g;
  $inlin =~ s/^ +//g;
  $inlin =~ s/\/sites\/mhnew.jwp.se\/files\///g;
  $inlin =~ s/\"\/images\//"_images\//g;


  print UT $inlin;
}

close(UT);
close(FIL);

@volumes = (
"User guide",
"Scripting manual",
"Reference manual",
"Contributors manual",
"Developer manual",
"Writers manual",
"MakeHuman and Blender guide",
"Makehuman history and evolution and beyond..."
);

foreach $volume (@volumes)
{
  $fn = $volume;
  $fn =~ s/ //g;
  $fn =~ s/&//g;

  system "xsltproc --stringparam volume '$volume' stylesheet.xsl unescaped.xml > rst/$fn.rst";
  system "sed -i -e 's/^[ ]\\*/\\*/g' rst/documentation.rst";

  chdir "rst";
  system "rst2pdf $fn.rst";
  chdir "..";
}

