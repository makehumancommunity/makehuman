<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

  <xsl:template match="u">
    <text:p text:style-name="Unimplemented">
      <xsl:value-of select="." />
    </text:p>
  </xsl:template>

  <xsl:template match="strong">
    <text:span text:style-name="STRONG">
      <xsl:value-of select="." />
    </text:span>
  </xsl:template>

  <xsl:template match="b">
    <text:span text:style-name="STRONG">
      <xsl:value-of select="." />
    </text:span>
  </xsl:template>

  <xsl:template match="em">
    <text:span text:style-name="EM">
      <xsl:value-of select="." />
    </text:span>
  </xsl:template>

  <xsl:template match="i">
    <text:span text:style-name="EM">
      <xsl:value-of select="." />
    </text:span>
  </xsl:template>

</xsl:stylesheet>

