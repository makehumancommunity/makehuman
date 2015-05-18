<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> 


  <xsl:template match="nodes">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="node">
    <xsl:variable name="sid" select="Sid" />
    <xsl:variable name="nid" select="Nid" />
    <xsl:variable name="title" select="title" />
    <xsl:variable name="root" select="'http://www.makehuman.org/node/'" />
    <xsl:for-each select="sectionbody">
      <xsl:for-each select=".//*[@class]">
        <xsl:value-of select="$root" /><xsl:value-of select="$sid" /><xsl:text> has a tag with a CLASS parameter.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//*[@style]">
        <xsl:value-of select="$root" /><xsl:value-of select="$sid" /><xsl:text> has a tag with a STYLE parameter.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//SPAN">
        <xsl:value-of select="$root" /><xsl:value-of select="$sid" /><xsl:text> contains a SPAN tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//DIV">
        <xsl:value-of select="$root" /><xsl:value-of select="$sid" /><xsl:text> contains a DIV tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//span">
        <xsl:value-of select="$root" /><xsl:value-of select="$sid" /><xsl:text> contains a SPAN tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//div">
        <xsl:value-of select="$root" /><xsl:value-of select="$sid" /><xsl:text> contains a DIV tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//h1">
        <xsl:value-of select="$root" /><xsl:value-of select="$sid" /><xsl:text> contains a H1 tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//H1">
        <xsl:value-of select="$root" /><xsl:value-of select="$sid" /><xsl:text> contains a H1 tag.
</xsl:text>
      </xsl:for-each>
    </xsl:for-each>
    <xsl:for-each select="Body">
      <xsl:if test="h3">
        <xsl:choose>
          <xsl:when test="h2" />
          <xsl:otherwise>
            <xsl:value-of select="$root" /><xsl:value-of select="$nid" /><xsl:text> has a H3 without having any H2.
</xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      
      <xsl:for-each select=".//*[@class]">
        <xsl:value-of select="$root" /><xsl:value-of select="$nid" /><xsl:text> has a tag with a CLASS parameter.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//*[@style]">
        <xsl:value-of select="$root" /><xsl:value-of select="$nid" /><xsl:text> has a tag with a STYLE parameter.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//SPAN">
        <xsl:value-of select="$root" /><xsl:value-of select="$nid" /><xsl:text> contains a SPAN tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//DIV">
        <xsl:value-of select="$root" /><xsl:value-of select="$nid" /><xsl:text> contains a DIV tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//span">
        <xsl:value-of select="$root" /><xsl:value-of select="$nid" /><xsl:text> contains a SPAN tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//div">
        <xsl:value-of select="$root" /><xsl:value-of select="$nid" /><xsl:text> contains a DIV tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//h1">
        <xsl:value-of select="$root" /><xsl:value-of select="$nid" /><xsl:text> contains a H1 tag.
</xsl:text>
      </xsl:for-each>
      <xsl:for-each select=".//H1">
        <xsl:value-of select="$root" /><xsl:value-of select="$nid" /><xsl:text> contains a H1 tag.
</xsl:text>
      </xsl:for-each>
    </xsl:for-each>
  </xsl:template>

  <xsl:output method="text" />

</xsl:stylesheet>

