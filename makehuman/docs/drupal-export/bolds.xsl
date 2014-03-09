<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

  <xsl:template match="i">
    <xsl:text> *</xsl:text>
    <xsl:value-of select="normalize-space(.)" />
    <xsl:text>* </xsl:text>
  </xsl:template>

  <xsl:template match="b">
    <xsl:text> **</xsl:text>
    <xsl:value-of select="normalize-space(.)" />
    <xsl:text>** </xsl:text>
  </xsl:template>

  <xsl:template match="strong">
    <xsl:text> **</xsl:text>
    <xsl:value-of select="normalize-space(.)" />
    <xsl:text>** </xsl:text>
  </xsl:template>


</xsl:stylesheet>

