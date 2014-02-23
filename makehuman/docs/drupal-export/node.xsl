<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

  <xsl:template match="node">

    <xsl:value-of select="title" />
    <xsl:text> (NID: </xsl:text>
    <xsl:value-of select="Nid" />
    <xsl:text> W: </xsl:text>
    <xsl:value-of select="sectionweight" />
<xsl:text>)
==============================================================================

</xsl:text>

      <xsl:apply-templates select="Body" />
  </xsl:template>

</xsl:stylesheet>

