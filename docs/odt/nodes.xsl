<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

  <xsl:template match="nodes">


    <xsl:text>
===========================
</xsl:text><xsl:value-of select="$volume" /><xsl:text>
===========================

</xsl:text>

    <xsl:for-each select="node[count(. | key('sectiontitles', Section)[1]) = 1]">
      <xsl:sort data-type="number" select="sectionweight"/>
    
      <xsl:variable name="sectnum" select="position()" />

<xsl:if test="Volume=$volume">
      <xsl:text>

.. raw:: pdf

   PageBreak

</xsl:text>\<xsl:copy-of select="$sectnum" /><xsl:text>. </xsl:text><xsl:value-of select="Section" /><xsl:text>
____________________________________________________________________________________________

</xsl:text>
<xsl:value-of select="sectionbody" />
    <xsl:text>

</xsl:text>

   
    <xsl:for-each select="key('sectiontitles', Section)">
      <xsl:sort data-type="number" select="weight" />      
    <xsl:text>

</xsl:text>
\<xsl:copy-of select="$sectnum" /><xsl:text>.</xsl:text><xsl:number level="multiple" value="position()" />
    <xsl:text> </xsl:text><xsl:value-of select="title" />
    <xsl:text> (NID: </xsl:text>
    <xsl:value-of select="Nid" />
<xsl:text>)
========================================================================================

</xsl:text>

      <xsl:apply-templates select="Body" />

    </xsl:for-each>
</xsl:if>

    </xsl:for-each>
  </xsl:template>

  <xsl:template match="sectionbody">
  </xsl:template>

</xsl:stylesheet>

