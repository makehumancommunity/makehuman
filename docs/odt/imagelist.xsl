<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> 

  <xsl:param name="volume" select="'User guide'"/>

  <xsl:strip-space elements="li"/>
  <xsl:preserve-space elements="pre"/>

  <xsl:key name="sectiontitles" match="node" use="Section" />

  <xsl:template match="document">
    <xsl:for-each select="//img">
      <xsl:value-of select="@src" /><xsl:text>
</xsl:text>
    </xsl:for-each>
  </xsl:template>

  <xsl:output method="text" />

</xsl:stylesheet>

