<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">

  <xsl:template match="BREAK">
    <text:line-break />
  </xsl:template>

  <xsl:template match="SPC">
    <text:s/>
  </xsl:template>

  <xsl:template match="TAB">
    <text:tab />
  </xsl:template>
  
  <xsl:template match="pre">
    <text:p text:style-name="code">
      <xsl:apply-templates />
    </text:p>
  </xsl:template>

</xsl:stylesheet>

